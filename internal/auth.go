package internal

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"database/sql"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"io"
	"net/http"
	"strings"
	"time"
)

func generateClientKey(sessionID string) error {
	// Generate RSA key pair
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return err
	}

	// Convert keys to PEM format
	privateKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: x509.MarshalPKCS1PrivateKey(privateKey),
	})
	spkiBytes, err := x509.MarshalPKIXPublicKey(&privateKey.PublicKey)
	if err != nil {
		return err
	}
	publicKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: spkiBytes,
	})
	timestamp := time.Now().Unix()
	// Store keys in the database
	writer := GetDatabaseWriter("db/data.db")
	err = writer.Write("INSERT INTO SessionKeys (sessionID, privateKey, publicKey,timestamp) VALUES (?, ?, ?, ?)",
		sessionID, privateKeyPEM, publicKeyPEM, timestamp)
	return err
}

func ServeClientPublicKey(w http.ResponseWriter, r *http.Request) {
	sessionID := r.URL.Query().Get("sessionID")
	if sessionID == "" {
		http.Error(w, "Missing sessionID", http.StatusBadRequest)
		return
	}

	var publicKey string
	vr := GetDatabaseValueRetriever("db/data.db")
	err := vr.RetrieveValue(&publicKey, `SELECT publicKey FROM SessionKeys WHERE sessionID = (?)`, sessionID)
	fmt.Printf(publicKey)
	if err != nil {
		err := generateClientKey(sessionID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		err = vr.RetrieveValue(&publicKey, `SELECT publicKey FROM SessionKeys WHERE sessionID = (?)`, sessionID)
	}

	w.Header().Set("Content-Type", "application/x-pem-file")
	_, err = w.Write([]byte(publicKey))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Printf("%x", publicKey)
}

// Store the decrypted AES key in the database for the client
func storeAESKey(clientID string, aesKey []byte) error {
	// Store the AES key in hex format
	aesKeyHex := hex.EncodeToString(aesKey)
	writer := GetDatabaseWriter("db/data.db")
	err := writer.Write("UPDATE SessionKeys SET aesKey = (?) WHERE sessionID = (?)", aesKeyHex, clientID)
	if err != nil {
		fmt.Printf(err.Error())
	}
	return err
}

// DecryptClientAESKey received from client and store it in the database
func DecryptClientAESKey(w http.ResponseWriter, r *http.Request) {
	clientID := r.URL.Query().Get("sessionID")
	if clientID == "" {
		http.Error(w, "Missing clientID", http.StatusBadRequest)
		return
	}

	// Retrieve the private key from the database
	var privateKeyPEM string
	vr := GetDatabaseValueRetriever("db/data.db")
	err := vr.RetrieveValue(&privateKeyPEM, "SELECT privateKey FROM SessionKeys WHERE sessionID = (?)", clientID)
	if err != nil {
		http.Error(w, "SessionID not found", http.StatusNotFound)
		return
	}

	// Decode PEM-encoded private key
	block, _ := pem.Decode([]byte(privateKeyPEM))
	if block == nil || block.Type != "RSA PRIVATE KEY" {
		http.Error(w, "Invalid private key format", http.StatusInternalServerError)
		return
	}
	privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		http.Error(w, "Failed to parse private key", http.StatusInternalServerError)
		return
	}

	// Read the encrypted AES key from the request body

	encryptedAESKey, err := io.ReadAll(r.Body)
	if err != nil {
		fmt.Printf("Failed to read encrypted AES key: %v\n", err)
		http.Error(w, "Failed to read encrypted AES key", http.StatusBadRequest)
		return
	}
	// Convert to base64 string
	base64String := base64.StdEncoding.EncodeToString(encryptedAESKey)
	fmt.Printf("Content-Length: %d\n", r.ContentLength)
	fmt.Printf("Actual-Length: %d\n", len(encryptedAESKey))
	fmt.Printf("Request Headers: %+v\n", r.Header)
	fmt.Printf("Key: %s\n", base64String)

	// Decrypt the AES key using the client's private key
	hash := sha256.New()
	aesKey, err := rsa.DecryptOAEP(hash, rand.Reader, privateKey, encryptedAESKey, nil)
	if err != nil {
		fmt.Printf("Failed to decrypt AES key. Error: %v\nEncrypted Key: %x\n", err, encryptedAESKey)
		http.Error(w, "Failed to decrypt AES key", http.StatusInternalServerError)
		return
	}

	// Store the AES key in the database
	if err := storeAESKey(clientID, aesKey); err != nil {
		fmt.Printf("Failed to store AES key. Error: %v\n", err)
		http.Error(w, "Failed to store AES key", http.StatusInternalServerError)
		return
	}

	_, err = fmt.Fprintf(w, "AES key stored successfully for client: %s", clientID)
	if err != nil {
		http.Error(w, "Failed to write response", http.StatusInternalServerError)
		return
	}
}

// Retrieve the AES key for a client
func getAESKey(clientID string) ([]byte, error) {
	var aesKeyHex string
	clientID = strings.ReplaceAll(clientID, "+", " ")
	vr := GetDatabaseValueRetriever("db/data.db")
	err := vr.RetrieveValue(&aesKeyHex, "SELECT aesKey FROM SessionKeys WHERE sessionID = (?)", clientID)
	if err != nil {
		fmt.Printf(err.Error())
		return nil, err
	}

	// Decode the hex format AES key to bytes
	aesKey, err := hex.DecodeString(aesKeyHex)
	return aesKey, err
}

func GetUser(w http.ResponseWriter, r *http.Request) string {
	// Retrieve the LoginID from the cookie
	cookie, err := r.Cookie("loginID")
	if err != nil {
		fmt.Printf("No session cookie found")
		return ""
	}
	LoginID := cookie.Value

	// Query the database to validate the LoginID and retrieve the username
	var username string
	vr := GetDatabaseValueRetriever("db/data.db")
	err = vr.RetrieveValue(&username, "SELECT Username FROM LoggedIn WHERE LoginID = (?)", LoginID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			fmt.Printf("invalid session")
			return ""
		}
		fmt.Printf(`Error:%v`, err)
		return ""
	}
	loginIDBytes := make([]byte, 16)
	_, err = rand.Read(loginIDBytes)
	if err != nil {
		fmt.Printf("failed to generate login ID: %v", err)
		return ""
	}
	loginID := hex.EncodeToString(loginIDBytes)

	timestamp := time.Now().Unix()
	writer := GetDatabaseWriter("db/data.db")
	err = writer.Write(`
		INSERT INTO LoggedIn (Username, LoginID, timestamp) 
		VALUES (?, ?, ?)
		ON CONFLICT(Username) DO UPDATE 
		SET LoginID = ?, timestamp = ?`,
		username, loginID, timestamp, loginID, timestamp)
	if err != nil {
		fmt.Printf("Failed to insert or update session: %v", err)
	}

	cookie = &http.Cookie{
		Name:     "loginID",
		Value:    loginID,
		Path:     "/",
		HttpOnly: true,  // Protect from JavaScript access
		Secure:   false, // Only send over HTTPS
		MaxAge:   3600,  // Optional: set expiration in seconds (1 hour here)
	}
	http.SetCookie(w, cookie)
	fmt.Println("Cookie Refreshed")
	return username
}

func Logout(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/", http.StatusSeeOther)
	// Retrieve the LoginID from the cookie
	cookie, err := r.Cookie("loginID")
	if err != nil {
		fmt.Printf("No session cookie found")
		return
	}
	LoginID := cookie.Value

	// Delete the logged in entry
	writer := GetDatabaseWriter("db/data.db")
	err = writer.Write(`DELETE FROM LoggedIn WHERE LoginID = ?`, LoginID)
	if err != nil {
		fmt.Printf(`Error:%v`, err)
		return
	}

}
func CheckRSAValidity(w http.ResponseWriter, r *http.Request) {
	body := r.URL.Query().Get("key")
	if body == "" {
		http.Error(w, "Requires Key as Parameter", http.StatusBadRequest)
		return
	}
	query := `SELECT EXISTS(SELECT 1 FROM SessionKeys WHERE SessionKeys.publicKey = ?)`
	checker := GetDatabaseExistenceChecker("db/data.db")
	exists, err := checker.ConcurrentCheckExist(query, body)
	if err != nil && !errors.Is(err, sql.ErrNoRows) {
		http.Error(w, "Failed to check RSA key", http.StatusInternalServerError)
		return
	}
	err = json.NewEncoder(w).Encode(exists)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
