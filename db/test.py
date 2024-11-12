import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# Define the category to check for duplicates
target_category = "clothesbin"

# Retrieve entries with the target RecycleItemCategory and check for duplicates
cursor.execute("""
    SELECT Latitude, Longitude
    FROM RecycleCategory
    WHERE RecycleItemCategory = ?
""", (target_category,))

# Fetch all matching rows
rows = cursor.fetchall()

# Prepare a list to store duplicates and their RecycleItemCategory
duplicates = []

# Loop through each row to find duplicates with the same Latitude and Longitude
for latitude, longitude in rows:
    # Retrieve entries with the same Latitude and Longitude but different RecycleItemCategory
    cursor.execute("""
        SELECT RecycleItemCategory
        FROM RecycleCategory
        WHERE Latitude = ? AND Longitude = ? AND RecycleItemCategory != ?
    """, (latitude, longitude, target_category))
    
    # Fetch duplicates
    duplicate_categories = cursor.fetchall()
    
    # If duplicates are found, add them to the list
    if duplicate_categories:
        duplicates.append({
            'Latitude': latitude,
            'Longitude': longitude,
            'DuplicateCategories': [category[0] for category in duplicate_categories]
        })

# Close the connection
connection.close()

# Print out the duplicates
if duplicates:
    print("Duplicates found for entries with RecycleItemCategory 'clothesbin':")
    for entry in duplicates:
        print(f"Location (Latitude: {entry['Latitude']}, Longitude: {entry['Longitude']}) has duplicates with categories: {entry['DuplicateCategories']}")
else:
    print("No duplicates found for entries with RecycleItemCategory 'clothesbin'.")