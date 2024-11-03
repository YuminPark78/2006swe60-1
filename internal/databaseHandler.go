package internal

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	_ "modernc.org/sqlite" // SQLite driver
	"reflect"
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
		if errors.Is(err, sql.ErrNoRows) {
			fmt.Println("No rows returned for the given sessionID")
			return fmt.Errorf("no rows found for the specified sessionID")
		}
		fmt.Printf("Error scanning single value: %v\n", err)
		return err
	}

	// Handle byte slice and convert to string
	switch v := value.(type) {
	case []byte:
		*dest = string(v) // Convert byte slice to string
	case string:
		*dest = v // Assign string directly
	default:
		return fmt.Errorf("unexpected type for database value: %T", v)
	}

	fmt.Printf("ConcurrentRetrieveValue completed with value: %s\n", *dest)
	return nil
}

// ConcurrentCheckExist checks if a given SELECT EXISTS query returns any rows and returns a boolean indicating the existence.
func (handler *DatabaseHandler) ConcurrentCheckExist(query string, args ...interface{}) (bool, error) {
	// Check if the query starts with "SELECT EXISTS"
	if !strings.HasPrefix(strings.ToUpper(strings.TrimSpace(query)), "SELECT EXISTS") {
		log.Printf("ConcurrentCheckExist only supports SELECT EXISTS queries. Query received: %s\n", query)
		return false, fmt.Errorf("ConcurrentCheckExist only supports SELECT EXISTS queries")
	}

	fmt.Printf("Starting ConcurrentCheckExist with query: %s, args: %v\n", query, args)

	var exists bool
	row := handler.db.QueryRow(query, args...)
	if err := row.Scan(&exists); err != nil {
		fmt.Printf("Error scanning existence check: %v\n", err)
		return false, err
	}

	fmt.Printf("ConcurrentCheckExist completed with result: %v\n", exists)
	return exists, nil
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

// WriteJSON accepts a table name and JSON data, validates it, and writes it to the table.
func (handler *DatabaseHandler) WriteJSON(tableName string, jsonData []byte) error {
	// Parse JSON into a map
	var dataMap map[string]interface{}
	err := json.Unmarshal(jsonData, &dataMap)
	if err != nil {
		return fmt.Errorf("failed to parse JSON: %v", err)
	}

	// Get the table schema (column names and order)
	columns, err := getTableColumns(handler.db, tableName)
	if err != nil {
		return fmt.Errorf("failed to get table schema: %v", err)
	}

	// Ensure JSON keys match the table columns
	jsonKeys := reflect.ValueOf(dataMap).MapKeys()
	jsonKeySet := make(map[string]struct{})
	for _, key := range jsonKeys {
		jsonKeySet[key.String()] = struct{}{}
	}
	for _, col := range columns {
		if _, exists := jsonKeySet[col]; !exists {
			return fmt.Errorf("JSON is missing required field: %s", col)
		}
	}

	// Generate SQL query and argument list
	var placeholders []string
	var args []interface{}
	for _, col := range columns {
		placeholders = append(placeholders, "?")
		args = append(args, dataMap[col])
	}
	query := fmt.Sprintf(`INSERT INTO %s (%s) VALUES (%s)`, tableName, strings.Join(columns, ", "), strings.Join(placeholders, ", "))

	// Call the original Write function
	return handler.Write(query, args...)
}

// Helper function to get the columns of a table
func getTableColumns(db *sql.DB, tableName string) ([]string, error) {
	query := fmt.Sprintf("PRAGMA table_info(%s);", tableName)
	rows, err := db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get table info: %v", err)
	}
	defer func(rows *sql.Rows) {
		err := rows.Close()
		if err != nil {
			fmt.Printf("Error closing rows: %v\n", err)
			return
		}
	}(rows)

	var columns []string
	for rows.Next() {
		var cid int
		var name, typ string
		var notnull, pk int
		var dfltValue interface{}
		if err := rows.Scan(&cid, &name, &typ, &notnull, &dfltValue, &pk); err != nil {
			return nil, fmt.Errorf("failed to scan table info: %v", err)
		}
		columns = append(columns, name)
	}
	return columns, nil
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
