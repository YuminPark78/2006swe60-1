package main

import (
	"database/sql"
	"log"
	"net/http"
	"test/internal"
	"time"
)

func cleanUpExpiredSessions(db *sql.DB) {
	// 30 minutes in seconds
	expiryTime := int64(30 * 60)

	// SQL query to delete sessions older than 30 minutes based on Unix timestamp
	query := `DELETE FROM LoggedIn WHERE Timestamp < (strftime('%s', 'now') - ?)`

	// Execute the query, passing expiryTime as the parameter
	result, err := db.Exec(query, expiryTime)
	if err != nil {
		log.Printf("Error cleaning up expired sessions: %v", err)
		return
	}

	query = `DELETE FROM SessionKeys WHERE Timestamp < (strftime('%s', 'now') - ?)`

	// Execute the query, passing expiryTime as the parameter
	result, err = db.Exec(query, expiryTime)
	if err != nil {
		log.Printf("Error cleaning up expired sessions: %v", err)
		return
	}

	// Check how many rows were affected (optional)
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		log.Printf("Error fetching affected rows: %v", err)
		return
	}
	log.Printf("Expired sessions cleaned up. Rows affected: %d\n", rowsAffected)
}

func main() {
	imagefileServer := http.FileServer(http.Dir("./images"))
	http.Handle("/images/", http.StripPrefix("/images/", imagefileServer))
	jsfileServer := http.FileServer(http.Dir("./js"))
	http.Handle("/js/", http.StripPrefix("/js/", jsfileServer))
	cssfileServer := http.FileServer(http.Dir("./css"))
	http.Handle("/css/", http.StripPrefix("/css/", cssfileServer))
	guidefileServer := http.FileServer(http.Dir("./guides"))
	http.Handle("/guides/", http.StripPrefix("/guides/", guidefileServer))
	// Serve HTML file (main page)
	http.HandleFunc("/map", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/MapPage.html")
	})
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/landing page.html")
	})
	http.HandleFunc("/recycleables", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/recylables.html")
	})
	http.HandleFunc("/ewaste", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/ewaste.html")
	})
	http.HandleFunc("/textiles", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/textile1.html")
	})
	http.HandleFunc("/textiles2", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/textile2.html")
	})
	http.HandleFunc("/login", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/Login.html")
	})
	http.HandleFunc("/final", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/FinalPage.html")
	})
	http.HandleFunc("/register", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/register.html")
	})
	http.HandleFunc("/bookmarkspage", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/BookmarksPage.html")
	})
	http.HandleFunc("/comments", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		http.ServeFile(w, r, "./web/pastcomments.html")
	})

	// Set up API endpoint for data
	http.HandleFunc("/mapapi/location", internal.GetLocation) // GET requests for location
	http.HandleFunc("/api/locationcomment/", internal.GetLocationComment)
	http.HandleFunc("/getkey", internal.ServeClientPublicKey)
	http.HandleFunc("/sendkey", internal.DecryptClientAESKey)
	http.HandleFunc("/loginattempt", internal.AttemptLogin)
	http.HandleFunc("/registerProcess", internal.RegisterUser)
	http.HandleFunc("/getUser", internal.GetUsername)
	http.HandleFunc("/logout", internal.Logout)
	http.HandleFunc("/getComments", internal.GetComments)
	http.HandleFunc("/getBookmarks", internal.GetBookmarks)
	http.HandleFunc("/addBookmark", internal.AddBookmark)
	http.HandleFunc("/addComment", internal.AddComment)
	http.HandleFunc("/checkRSA", internal.CheckRSAValidity)

	// Start the server
	log.Println("Server starting on http://localhost:8080")
	log.Println(http.ListenAndServe(":8080", nil))
	ticker := time.NewTicker(10 * time.Minute)
	defer ticker.Stop()

	// Run cleanup immediately on startup
	db := internal.GetDatabaseHandler("db/data.db")
	go db.CleanUpExpiredSessions()
	defer internal.CloseAllDatabaseHandlers()
	// Periodically run cleanup function on every tick
	go func() {
		for range ticker.C {
			db.CleanUpExpiredSessions()
		}
	}()
} // Also, you can try interactive lessons for GoLand by selecting 'Help | Learn IDE Features' from the main menu.
