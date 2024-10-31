package internal

import (
	"database/sql"
	"fmt"
	"log"
	_ "modernc.org/sqlite" // SQLite driver
	"strings"
	"sync"
)

var (
	dbHandlers     = make(map[string]*DatabaseHandler) // Map to store DatabaseHandler instances by database name
	dbHandlersLock sync.Mutex                          // Mutex to synchronize access to dbHandlers map
)

// DatabaseHandler manages the database connection and operations
type DatabaseHandler struct {
	db      *sql.DB
	writeCh chan WriteRequest
	wg      sync.WaitGroup
}

// WriteRequest represents a queued write request
type WriteRequest struct {
	Query string
	Args  []interface{}
	Done  chan error
}

// GetDatabaseHandler returns a singleton DatabaseHandler for a specific database
func GetDatabaseHandler(dataSourceName string) *DatabaseHandler {
	dbHandlersLock.Lock() // Lock to safely access the map
	defer dbHandlersLock.Unlock()

	// Check if the handler already exists for this database
	if handler, exists := dbHandlers[dataSourceName]; exists {
		fmt.Printf("Using existing DatabaseHandler for database: %s\n", dataSourceName)
		return handler
	}

	// Create a new DatabaseHandler if it doesn’t exist
	handler, err := NewDatabaseHandler(dataSourceName)
	if err != nil {
		log.Fatalf("Failed to initialize database handler for %s: %v\n", dataSourceName, err)
	}

	dbHandlers[dataSourceName] = handler // Store the new handler in the map
	fmt.Printf("Created new DatabaseHandler for database: %s\n", dataSourceName)
	return handler
}

// NewDatabaseHandler initializes a DatabaseHandler with a database connection and write queue
func NewDatabaseHandler(dataSourceName string) (*DatabaseHandler, error) {
	db, err := sql.Open("sqlite", dataSourceName)
	if err != nil {
		log.Printf("Failed to open database: %v\n", err)
		return nil, err
	}

	// Enable WAL mode and check the result
	var mode string
	err = db.QueryRow("PRAGMA journal_mode=WAL;").Scan(&mode)
	if err != nil || mode != "wal" {
		log.Printf("Failed to set WAL mode, got mode: %v, error: %v\n", mode, err)
		err := db.Close()
		if err != nil {
			return nil, err
		}
		return nil, err
	}

	fmt.Printf("Journal mode successfully set to WAL for database: %s\n", dataSourceName)

	// Set connection pool limits for WAL mode
	db.SetMaxOpenConns(7) // Allows multiple concurrent connections for reads
	db.SetMaxIdleConns(4) // Keeps a few idle connections ready for quick access

	handler := &DatabaseHandler{
		db:      db,
		writeCh: make(chan WriteRequest),
	}

	handler.wg.Add(1)
	go handler.writeProcessor()

	fmt.Printf("DatabaseHandler created with WAL mode for database: %s\n", dataSourceName)
	return handler, nil
}

// isSelectQuery checks if a query string starts with "SELECT" (case-insensitive)
func isSelectQuery(query string) bool {
	trimmedQuery := strings.TrimSpace(query)
	return strings.HasPrefix(strings.ToUpper(trimmedQuery), "SELECT")
}

// ConcurrentRead performs a read operation, validating the query to ensure it’s a SELECT statement
func (handler *DatabaseHandler) ConcurrentRead(query string, args ...interface{}) ([]map[string]string, error) {
	if !isSelectQuery(query) {
		log.Printf("ConcurrentRead only supports SELECT queries. Query received: %s\n", query)
		return nil, fmt.Errorf("ConcurrentRead only supports SELECT queries")
	}

	fmt.Printf("Starting ConcurrentRead with query: %s, args: %v\n", query, args)

	rows, err := handler.db.Query(query, args...)
	if err != nil {
		fmt.Printf("Error executing query: %v\n", err)
		return nil, err
	}
	defer func(rows *sql.Rows) {
		err := rows.Close()
		if err != nil {
			fmt.Printf("Error closing rows: %v\n", err)
			return
		}
	}(rows)

	columns, err := rows.Columns()
	if err != nil {
		fmt.Printf("Error fetching columns: %v\n", err)
		return nil, err
	}

	var results []map[string]string
	for rows.Next() {
		// Create a slice of interface{} to hold each column value
		row := make([]interface{}, len(columns))
		rowPointers := make([]interface{}, len(columns))
		for i := range row {
			rowPointers[i] = &row[i]
		}

		// Scan the row into the rowPointers
		if err := rows.Scan(rowPointers...); err != nil {
			fmt.Printf("Error scanning row: %v\n", err)
			return nil, err
		}

		// Convert each value to a string and add it to the row map
		rowMap := make(map[string]string)
		for i, col := range columns {
			// Convert each column value to a string
			if row[i] != nil {
				rowMap[col] = fmt.Sprintf("%v", row[i]) // Convert to string using fmt.Sprintf
			} else {
				rowMap[col] = "" // Handle NULL values by setting them to an empty string
			}
		}
		results = append(results, rowMap)
	}

	if err = rows.Err(); err != nil {
		fmt.Printf("Error iterating rows: %v\n", err)
		return nil, err
	}

	fmt.Printf("ConcurrentRead completed with results: %v\n", results)
	return results, nil
}

// ConcurrentRetrieveValue performs a read operation, validating the query to ensure it’s a SELECT statement
func (handler *DatabaseHandler) ConcurrentRetrieveValue(dest *string, query string, args ...interface{}) error {
	if !isSelectQuery(query) {
		log.Printf("ConcurrentRetrieveValue only supports SELECT queries. Query received: %s\n", query)
		return fmt.Errorf("ConcurrentRetrieveValue only supports SELECT queries")
	}

	fmt.Printf("Starting ConcurrentRetrieveValue with query: %s, args: %v\n", query, args)

	var value interface{}
	row := handler.db.QueryRow(query, args...)
	if err := row.Scan(&value); err != nil {
		fmt.Printf("Error scanning single value: %v\n", err)
		return err
	}

	// Convert the value to a string and assign it to dest
	if value != nil {
		*dest = fmt.Sprintf("%v", value) // Convert to string using fmt.Sprintf
	} else {
		*dest = "" // Handle NULL values by setting dest to an empty string
	}

	fmt.Printf("ConcurrentRetrieveValue completed with value: %s\n", *dest)
	return nil
}

// writeProcessor processes each write request sequentially
func (handler *DatabaseHandler) writeProcessor() {
	defer handler.wg.Done()
	for req := range handler.writeCh {
		fmt.Printf("Processing Write request: %s, args: %v\n", req.Query, req.Args)

		_, err := handler.db.Exec(req.Query, req.Args...)
		req.Done <- err
		close(req.Done)

		fmt.Printf("Write request completed with error: %v\n", err)
	}
}

// Write enqueues a write request, which is processed sequentially by writeProcessor
func (handler *DatabaseHandler) Write(query string, args ...interface{}) error {
	req := WriteRequest{
		Query: query,
		Args:  args,
		Done:  make(chan error, 1),
	}

	fmt.Printf("Enqueuing Write request: %s, args: %v\n", query, args)
	handler.writeCh <- req

	err := <-req.Done
	if err != nil {
		fmt.Printf("Write operation failed: %v\n", err)
	} else {
		fmt.Println("Write operation completed successfully")
	}
	return err
}

// CloseAllDatabaseHandlers closes all open DatabaseHandler instances
func CloseAllDatabaseHandlers() {
	dbHandlersLock.Lock()
	defer dbHandlersLock.Unlock()

	for name, handler := range dbHandlers {
		fmt.Printf("Closing DatabaseHandler for database: %s\n", name)
		err := handler.Close()
		if err != nil {
			fmt.Printf("Error closing database %s: %v\n", name, err)
			return
		}
		delete(dbHandlers, name) // Remove the handler from the map
	}
}

// Close gracefully shuts down DatabaseHandler
func (handler *DatabaseHandler) Close() error {
	close(handler.writeCh)
	handler.wg.Wait()
	fmt.Println("DatabaseHandler closed")
	return handler.db.Close()
}
