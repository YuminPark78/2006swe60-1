import sqlite3

# Connect to the database
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Delete entries with RecycleItemCategory as "RecyclingBin"
cursor.execute("""
    DELETE FROM RecycleCategory
    WHERE RecycleItemCategory = 'RecyclingBin'
""")

# Commit the changes and close the connection
deleted_count = cursor.rowcount
conn.commit()
conn.close()

print(f"Deleted {deleted_count} entries with RecycleItemCategory as 'RecyclingBin'.")