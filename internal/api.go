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
	"golang.org/x/crypto/bcrypt"
	"io"
	"net/http"
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
	// Send the results as JSON
	err = json.NewEncoder(w).Encode(rows)
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
	db := GetDatabaseHandler("db/data.db")
	rows, err := db.ConcurrentRead(
		`SELECT Comments.*
		FROM Comments
		WHERE Comments.Latitude = ? AND Comments.Longitude =?`, lat, long)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	// Send the results as JSON
	err = json.NewEncoder(w).Encode(rows)
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
	db := GetDatabaseHandler("db/data.db")
	// Execute the query and scan the result into the hashedPassword variable
	err = db.ConcurrentRetrieveValue(&hashedPassword, query, username)
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
	err = db.ConcurrentRetrieveValue(&salt, query, username)
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
	err = db.Write(`
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
	response := map[string]string{"username": username}
	err := json.NewEncoder(w).Encode(response)
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
	db := GetDatabaseHandler("db/data.db")
	rows, err := db.ConcurrentRead(`
        SELECT c.Date, l.Name AS Location, c.Comment
        FROM Comments c
        JOIN Locations l ON c.Latitude = l.Latitude AND c.Longitude = l.Longitude
        WHERE c.Username = ?`, username)
	if err != nil {
		fmt.Printf("Failed to retrieve data: %v", err)
		return
	}
	if len(rows) < 1 {
		fmt.Printf("No Comments")
		err = json.NewEncoder(w).Encode("You haven't commented")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		return
	}
	err = json.NewEncoder(w).Encode(rows)
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
	db := GetDatabaseHandler("db/data.db")
	rows, err := db.ConcurrentRead(`
        SELECT l.Name AS Name, l.Address AS Address, l.Latitude AS Latitude, l.Longitude AS Longitude
        FROM Bookmarks b
        JOIN Locations l ON b.Latitude = l.Latitude AND b.Longitude = l.Longitude
        WHERE b.Username = ?`, username)
	if err != nil {
		fmt.Printf("Failed to retrieve data: %v", err)
		return
	}
	if len(rows) < 1 {
		err := json.NewEncoder(w).Encode("You have no bookmarks")
		if err != nil {
			return
		}
		return
	}
	err = json.NewEncoder(w).Encode(rows)
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
	db := GetDatabaseHandler("db/data.db")
	err = db.Write(`
        INSERT INTO Bookmarks (Username, Latitude, Longitude)
        VALUES (?, ?, ?)`, username, coords.Lat, coords.Long)

	if err != nil {
		fmt.Printf("failed to insert bookmark: %s", err.Error())
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
		fmt.Printf("Not Logged In")
		return
	}
	var date = time.Now().Format("2006-01-02")
	db := GetDatabaseHandler("db/data.db")
	err = db.Write(`
        INSERT INTO Comments (Username, Latitude, Longitude, Comment, Date)
        VALUES (?, ?, ?, ?, ?)`, username, comment.Lat, comment.Long, comment.Comment, date)

	if err != nil {
		fmt.Printf("failed to insert comment: %s", err.Error())
		return
	}
	return
}
