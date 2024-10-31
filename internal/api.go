package internal

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"database/sql"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
	"io"
	"net/http"
	"strconv"
	"time"
)

// Location struct to represent data from the SQLite table
type Location struct {
	Name         string  `json:"Name"`
	OpeningHours string  `json:"Opening Hours"`
	Address      string  `json:"Address"`
	Longitude    float64 `json:"Longitude"`
	Latitude     float64 `json:"Latitude"`
}

type Comment struct {
	Longitude float64 `json:"Longitude"`
	Latitude  float64 `json:"Latitude"`
	Username  string  `json:"Username"`
	Comment   string  `json:"Comment"`
	Date      string  `json:"Date"`
}

// GetLocation handles GET requests to /api/location
func GetLocation(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	// Example query to get all locations
	// Extract the category parameter from the query
	category := r.URL.Query().Get("category")

	// Check if the category is provided
	if category == "" {
		http.Error(w, "Category parameter is required", http.StatusBadRequest)
		return
	}
	db := GetDatabaseHandler("db/data.db")
	// Use a parameterized query to safely insert the category
	rows, err := db.ConcurrentRead(
		`SELECT Locations.*
		FROM Locations
		JOIN RecycleCategory 
		ON Locations.Latitude = RecycleCategory.Latitude 
		AND Locations.Longitude = RecycleCategory.Longitude
		WHERE RecycleCategory.RecycleItemCategory = ?`, category)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// Create a slice to hold the results
	var locations []Location
	for _, row := range rows {
		Name := row["Name"]
		OpeningHours := row["Opening Hours"]
		Address := row["Address"]
		Longitude, _ := strconv.ParseFloat(row["Longitude"], 64)
		Latitude, _ := strconv.ParseFloat(row["Latitude"], 64)
		loc := Location{Longitude: Longitude, Latitude: Latitude, Name: Name, OpeningHours: OpeningHours, Address: Address}
		locations = append(locations, loc)
	}

	// Send the results as JSON
	err = json.NewEncoder(w).Encode(locations)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetLocationComment(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	// Example query to get all locations
	// Extract the category parameter from the query
	lat := r.URL.Query().Get("lat")
	long := r.URL.Query().Get("long")

	// Check if the category is provided
	if lat == "" || long == "" {
		http.Error(w, "Coordinate parameters required", http.StatusBadRequest)
		return
	}

	// Use a parameterized query to safely insert the category
	rows, err := DB.Query(
		`SELECT Comments.*
		FROM Comments
		WHERE Comments.Latitude = ? AND Comments.Longitude =?`, lat, long)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer func(rows *sql.Rows) {
		err := rows.Close()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	}(rows)

	// Create a slice to hold the results
	var comments []Comment
	for rows.Next() {
		var loc Comment
		if err := rows.Scan(&loc.Latitude, &loc.Longitude, &loc.Username, &loc.Comment, &loc.Date); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		comments = append(comments, loc)
	}

	// Send the results as JSON
	err = json.NewEncoder(w).Encode(comments)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func AttemptLogin(w http.ResponseWriter, r *http.Request) {
	type EncryptedDataRequest struct {
		SessionID  string `json:"sessionid"`
		Username   string `json:"username"`
		Ciphertext string `json:"ciphertext"`
		IV         string `json:"iv"`
	}
	var req EncryptedDataRequest

	// Parse the JSON body
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Base64 decode the ciphertext and IV
	ciphertext, err := base64.StdEncoding.DecodeString(req.Ciphertext)
	if err != nil {
		http.Error(w, "Invalid base64 ciphertext", http.StatusBadRequest)
		return
	}

	iv, err := base64.StdEncoding.DecodeString(req.IV)
	if err != nil {
		http.Error(w, "Invalid base64 IV", http.StatusBadRequest)
		return
	}

	// Now you have the username, ciphertext (byte slice), and IV (byte slice)
	fmt.Printf("SessionID: %s\n", req.SessionID)
	fmt.Printf("Username: %s\n", req.Username)
	fmt.Printf("Ciphertext: %x\n", ciphertext) // Print ciphertext in hex
	fmt.Printf("IV: %x\n", iv)                 // Print IV in hex

	key, err := getAESKey(req.SessionID)
	if err != nil {
		fmt.Printf("Failed to retrieve AES key. Error: %v\n", err)
		return
	}
	// Step 1: Create a new AES cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		fmt.Printf("failed to create AES cipher: %v", err)
		return
	}

	// Step 2: Create a GCM cipher mode (Galois/Counter Mode)
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		fmt.Printf("failed to create GCM mode: %v", err)
		return
	}

	// Step 3: Decrypt the ciphertext using the GCM cipher and the IV
	// gcm.Open expects the IV, ciphertext, and additional data (nil if not used)
	plaintext, err := gcm.Open(nil, iv, ciphertext, nil)
	if err != nil {
		fmt.Printf("failed to decrypt: %v", err)
		return
	}

	// Step 2: Convert the byte array back to the original string
	password := plaintext
	username := req.Username
	fmt.Printf("Original string: %x\n", password)

	var hashedPassword string
	// SQL query to retrieve the hashed password for the given username
	query := `SELECT hashedPassword FROM Users WHERE username = ?`

	// Execute the query and scan the result into the hashedPassword variable
	err = DB.QueryRow(query, username).Scan(&hashedPassword)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			fmt.Printf("username %s not found", username)
			http.Error(w, "Username not found", http.StatusBadRequest)
			// Username doesn't exist
			return
		}
		fmt.Println(err) // Some other error occurred
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Printf("Hashed Password Retrieved: %s\n", hashedPassword)

	var salt string
	query = `SELECT salt FROM Users WHERE username = ?`
	err = DB.QueryRow(query, username).Scan(&salt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			fmt.Printf("username %s not found", username) // Username doesn't exist
			http.Error(w, "Username not found", http.StatusBadRequest)
			return
		}
		fmt.Println(err) // Some other error occurred
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Printf("Hashed Password Retrieved: %s\n", hashedPassword)
	hashedPasswordBytes, err := hex.DecodeString(hashedPassword)
	if err != nil {
		fmt.Printf("failed to decode hex string of password: %v", err)
		http.Error(w, "failed to decode hex string of password", http.StatusInternalServerError)
		return
	}
	saltBytes, err := hex.DecodeString(salt)
	if err != nil {
		fmt.Printf("failed to decode hex string of salt: %v", err)
		http.Error(w, "failed to decode hex string of salt", http.StatusInternalServerError)
		return
	}
	err = bcrypt.CompareHashAndPassword(hashedPasswordBytes, append(saltBytes, password...))
	if err != nil {
		fmt.Printf("Password mismatch %v", err)
		http.Error(w, `Password mismatch`, http.StatusBadRequest)
		return
	}

	loginIDBytes := make([]byte, 16)
	_, err = rand.Read(loginIDBytes)
	if err != nil {
		fmt.Printf("failed to generate login ID: %v", err)
		http.Error(w, "failed to generate login ID", http.StatusInternalServerError)
		return
	}
	loginID := hex.EncodeToString(loginIDBytes)

	timestamp := time.Now().Unix()
	_, err = DB.Exec(`
		INSERT INTO LoggedIn (Username, LoginID, timestamp) 
		VALUES (?, ?, ?)
		ON CONFLICT(Username) DO UPDATE 
		SET LoginID = ?, timestamp = ?`,
		username, loginID, timestamp, loginID, timestamp)
	if err != nil {
		fmt.Printf("Failed to insert or update session: %v", err)
		http.Error(w, "Failed to insert or update session", http.StatusInternalServerError)
	}

	cookie := &http.Cookie{
		Name:     "loginID",
		Value:    loginID,
		Path:     "/",
		HttpOnly: true,  // Protect from JavaScript access
		Secure:   false, // Only send over HTTPS
		MaxAge:   3600,  // Optional: set expiration in seconds (1 hour here)
	}
	http.SetCookie(w, cookie)
	fmt.Println("Cookie Set")

	// Respond with a success message
	_, err = w.Write([]byte("Data received successfully"))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetUsername(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	username := GetUser(w, r)
	if username == "" {
		http.Error(w, `Not Logged In`, http.StatusBadRequest)
		return
	}
	err := json.NewEncoder(w).Encode(username)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetComments(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	username := GetUser(w, r)
	if username == "" {
		http.Error(w, `Not Logged In`, http.StatusBadRequest)
		return
	}
	type Comment struct {
		Date     string `json:"date"`
		Location string `json:"location"`
		Comment  string `json:"comment"`
	}
	rows, err := DB.Query(`
        SELECT c.Date, l.Name AS Location, c.Comment
        FROM Comments c
        JOIN Locations l ON c.Latitude = l.Latitude AND c.Longitude = l.Longitude
        WHERE c.Username = ?`, username)
	if err != nil {
		fmt.Printf("Failed to retrieve data: %v", err)
		return
	}
	defer func(rows *sql.Rows) {
		err := rows.Close()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	}(rows)

	var found = false
	var comments []Comment
	for rows.Next() {
		var comment Comment
		if err := rows.Scan(&comment.Date, &comment.Location, &comment.Comment); err != nil {
			return
		}
		comments = append(comments, comment)
		found = true
	}

	if err = rows.Err(); err != nil {
		fmt.Printf("Failed to parse data: %v", err)
		return
	}
	if !found {
		err := json.NewEncoder(w).Encode("You haven't commented!")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		return
	}
	err = json.NewEncoder(w).Encode(comments)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func GetBookmarks(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	username := GetUser(w, r)
	if username == "" {
		http.Error(w, `Not Logged In`, http.StatusBadRequest)
		return
	}
	type Bookmark struct {
		Name      string `json:"name"`
		Address   string `json:"address"`
		Latitude  string `json:"latitude"`
		Longitude string `json:"longitude"`
	}
	rows, err := DB.Query(`
        SELECT l.Name AS Name, l.Address AS Address, l.Latitude AS Latitude, l.Longitude AS Longitude
        FROM Bookmarks b
        JOIN Locations l ON b.Latitude = l.Latitude AND b.Longitude = l.Longitude
        WHERE b.Username = ?`, username)
	if err != nil {
		fmt.Printf("Failed to retrieve data: %v", err)
		return
	}
	defer func(rows *sql.Rows) {
		err := rows.Close()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	}(rows)

	var found = false
	var bookmarks []Bookmark
	for rows.Next() {
		var bookmark Bookmark
		if err := rows.Scan(&bookmark.Name, &bookmark.Address, &bookmark.Latitude, &bookmark.Longitude); err != nil {
			return
		}
		bookmarks = append(bookmarks, bookmark)
		found = true
	}

	if err = rows.Err(); err != nil {
		fmt.Printf("Failed to parse data: %v", err)
		return
	}
	if !found {
		err := json.NewEncoder(w).Encode("You have no bookmarks")
		if err != nil {
			return
		}
		return
	}
	err = json.NewEncoder(w).Encode(bookmarks)
	if err != nil {
		return
	}
}

func AddBookmark(w http.ResponseWriter, r *http.Request) {
	// Ensure the request method is POST
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Read the body of the request
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
		return
	}
	type Coordinates struct {
		Lat  string `json:"lat"`
		Long string `json:"long"`
	}
	// Parse the JSON payload into the Coordinates struct
	var coords Coordinates
	err = json.Unmarshal(body, &coords)
	if err != nil {
		http.Error(w, "Error parsing JSON", http.StatusBadRequest)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	username := GetUser(w, r)
	if username == "" {
		http.Error(w, `Not Logged In`, http.StatusBadRequest)
		return
	}
	// Check if the category is provided
	if coords.Lat == "" || coords.Long == "" {
		http.Error(w, "Coordinate parameters required", http.StatusBadRequest)
		return
	}
	_, err = DB.Exec(`
        INSERT INTO Bookmarks (Username, Latitude, Longitude)
        VALUES (?, ?, ?)`, username, coords.Lat, coords.Long)

	if err != nil {
		var sqliteErr sqlite3.Error
		if errors.As(err, &sqliteErr) && errors.Is(sqliteErr.ExtendedCode, sqlite3.ErrConstraintUnique) {
			fmt.Printf("bookmark already exists for username: %s", username)
			return
		}
		fmt.Printf("failed to insert bookmark: %w", err)
		return
	}
	return
}

func AddComment(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
	}
	type Comment struct {
		Lat     string `json:"lat"`
		Long    string `json:"long"`
		Comment string `json:"comment"`
	}
	var comment Comment
	err = json.Unmarshal(body, &comment)
	if err != nil {
		http.Error(w, "Error parsing JSON", http.StatusBadRequest)
	}
	w.Header().Set("Content-Type", "application/json")
	username := GetUser(w, r)
	if username == "" {
		http.Error(w, `Not Logged In`, http.StatusBadRequest)
	}
	var date = time.Now().Format("2006-01-02")
	_, err = DB.Exec(`
        INSERT INTO Comments (Username, Latitude, Longitude, Comment, Date)
        VALUES (?, ?, ?, ?, ?)`, username, comment.Lat, comment.Long, comment.Comment, date)

	if err != nil {
		fmt.Printf("failed to insert bookmark: %w", err)
		return
	}
	return
}
