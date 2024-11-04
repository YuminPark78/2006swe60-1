package internal

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"golang.org/x/crypto/bcrypt"
	"log"
	"net/http"
	"strings"
)

// RegisterUser handles user registration requests
func RegisterUser(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	// Parse the JSON body
	var req struct {
		SessionID  string `json:"sessionid"`
		Username   string `json:"username"`
		Ciphertext string `json:"ciphertext"`
		IV         string `json:"iv"`
		Email      string `json:"email"`
	}

	// Decode the JSON Body
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		fmt.Println(err)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		err := json.NewEncoder(w).Encode(map[string]interface{}{
			"success": false,
			"message": "Invalid request body",
		})
		if err != nil {
			fmt.Println(err)
			return
		}
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

	username := req.Username
	password := string(plaintext)
	email := req.Email

	salt := make([]byte, 4)
	_, err = rand.Read(salt)
	if err != nil {
		fmt.Println(err)
		return
	}

	// Hash the password using bcrypt
	hashedPassword, err := bcrypt.GenerateFromPassword(append(salt, []byte(password)...), bcrypt.DefaultCost)
	if err != nil {
		http.Error(w, "Error hashing password", http.StatusInternalServerError)
		return
	}

	// Insert the new user into the database
	db := GetDatabaseHandler("db/data.db")
	err = db.Write("INSERT INTO Users (username, hashedPassword, salt, email) VALUES (?, ?, ?, ?)", username, hex.EncodeToString(hashedPassword), hex.EncodeToString(salt), email)
	if err != nil {
		log.Printf("SQL Insert Error: %v", err)

		if strings.Contains(err.Error(), "UNIQUE constraint failed") {
			if strings.Contains(err.Error(), "Users.username") {
				w.WriteHeader(http.StatusBadRequest)
				err := json.NewEncoder(w).Encode(map[string]interface{}{
					"success": false,
					"message": "Username already taken",
				})
				if err != nil {
					fmt.Println(err)
					return
				}
			} else if strings.Contains(err.Error(), "Users.email") {
				w.WriteHeader(http.StatusBadRequest)
				err := json.NewEncoder(w).Encode(map[string]interface{}{
					"success": false,
					"message": "Email already taken",
				})
				if err != nil {
					fmt.Println(err)
					return
				}
			} else {
				w.WriteHeader(http.StatusBadRequest)
				err := json.NewEncoder(w).Encode(map[string]interface{}{
					"success": false,
					"message": "Unknown SQL error",
				})
				if err != nil {
					fmt.Println(err)
					return
				}
			}
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	err = json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "User registered successfully!",
	})
	if err != nil {
		fmt.Println(err)
		return
	}
}
