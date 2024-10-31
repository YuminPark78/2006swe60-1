import requests
import sqlite3
import time
from tqdm import tqdm

# OneMap API endpoint and database connection
API_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
DB_PATH = "data.db"  # Replace with your actual database path

# List of postal codes
postal_codes = [
    "467360", "188021", "059413", "538766", "769098",
    "238839", "529536", "129588", "797653", "608532"
]

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Loop through each postal code and retrieve data
for postal_code in postal_codes:
    # Prepare API parameters
    params = {
        "searchVal": postal_code,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": "1"
    }
    
    try:
        # Send request to OneMap API
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        # Check if search results are available
        if data["found"] > 0:
            result = data["results"][0]  # Take the first result
            address = result.get("ADDRESS", "Unknown")
            latitude = float(result["LATITUDE"])
            longitude = float(result["LONGITUDE"])

            # Use address as the building name with "Clothes Bin" appended
            name = f"{address} Refash"
            opening_hours = "All time year round"

            # Insert or replace in Locations table
            cursor.execute("""
                SELECT COUNT(*) FROM Locations WHERE Latitude = ? AND Longitude = ?
            """, (latitude, longitude))
            exists_location = cursor.fetchone()[0] > 0

            if exists_location:
                # Update existing entry
                cursor.execute("""
                    UPDATE Locations
                    SET Name = ?, "Opening Hours" = ?, Address = ?
                    WHERE Latitude = ? AND Longitude = ?
                """, (name, opening_hours, address, latitude, longitude))
                print(f"Entry for postal code {postal_code} ({address}) has been replaced in Locations.")
            else:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO Locations (Name, "Opening Hours", Address, Latitude, Longitude)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, opening_hours, address, latitude, longitude))
                print(f"Entry for postal code {postal_code} ({address}) has been added to Locations.")

    except requests.RequestException as e:
        print(f"Error fetching data for postal code {postal_code}: {e}")
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {e}")

# Commit and close database connection
conn.commit()
conn.close()

print("Data retrieval and insertion complete.")