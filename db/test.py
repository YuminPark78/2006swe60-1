import requests
import sqlite3
import tqdm

mall_data = [
    {"Mall Name": "Aperia Mall", "Address": "12 KALLANG AVENUE", "Postal Code": "339511", "Additional Information": "Level 1 Lobby A"},
    {"Mall Name": "Ascent", "Address": "2 SCIENCE PARK DRIVE", "Postal Code": "118222", "Additional Information": "Level 1 Retail Lift Lobby"},
    {"Mall Name": "Bedok Mall", "Address": "311 New Upper Changi Rd", "Postal Code": "467360", "Additional Information": "B2 Linkway to MRT"},
    {"Mall Name": "Bishan Sports Centre", "Address": "5 Bishan Street 14", "Postal Code": "579783", "Additional Information": "Sport Centre Drop Off Lobby"},
    {"Mall Name": "Bugis +", "Address": "201 Victoria Street", "Postal Code": "188067", "Additional Information": "L1 External Walkway @ B+, facing Bugis Street"},
    {"Mall Name": "Bukit Gombak Sports Centre", "Address": "810 Bukit Batok West Ave 5", "Postal Code": "659088", "Additional Information": "L1 near Staircase A"},
    {"Mall Name": "Bukit Panjang Plaza", "Address": "1 Jelebu Rd", "Postal Code": "677743", "Additional Information": "L1 External Walkway outside dental clinic"},
    {"Mall Name": "Choa Chu Kang Sports Centre", "Address": "1 Choa Chu Kang St 53", "Postal Code": "689236", "Additional Information": "L1 near vehicle drop off point"},
    {"Mall Name": "Funan", "Address": "107 North Bridge Rd", "Postal Code": "179105", "Additional Information": "L3 near entrance to Courts"},
    {"Mall Name": "Galaxis", "Address": "1 Fusionopolis Place", "Postal Code": "138522", "Additional Information": "Level 1 Retail Walkway near escalator"},
    {"Mall Name": "Geylang Bahru Blk 68", "Address": "Blk 68 Geylang Bahru", "Postal Code": "330068", "Additional Information": "Void deck next to 7-11 Store"},
    {"Mall Name": "Geylang East Swimming Complex", "Address": "601 Aljunied Ave 1", "Postal Code": "389862", "Additional Information": "At entrance to swimming complex"},
    {"Mall Name": "Heartbeat @ Bedok", "Address": "11 Bedok North Street 1", "Postal Code": "469662", "Additional Information": "Level 1 beside Lift Lobby B"},
    {"Mall Name": "Hougang Sports Centre", "Address": "93 Hougang Avenue 4", "Postal Code": "538832", "Additional Information": "At entrance to Stadium"},
    {"Mall Name": "Jalan Besar Sports Centre", "Address": "100 Tyrwhitt Rd", "Postal Code": "207542", "Additional Information": "Walkway to Stadium Entrance"},
    {"Mall Name": "Jurong East Sports Centre", "Address": "21 Jurong East Street 31", "Postal Code": "609517", "Additional Information": "L2 South Entrance"},
    {"Mall Name": "Lot 1", "Address": "21 Choa Chu Kang Ave 4", "Postal Code": "689812", "Additional Information": "L1 Green Corner"},
    {"Mall Name": "Ngee Ann Polytechnic", "Address": "535 Clementi Road", "Postal Code": "599489", "Additional Information": "Block 22, Outside Food Club Canteen"},
    {"Mall Name": "Plaza 8", "Address": "1 Changi Business Park, Crescent", "Postal Code": "486025", "Additional Information": "Level 1 Podium C, near #01-25"},
    {"Mall Name": "Raffles City", "Address": "252 NORTH BRIDGE RD", "Postal Code": "179103", "Additional Information": "Basement 2 (carpark), Lobby A"},
    {"Mall Name": "Resorts World Sentosa", "Address": "8 Sentosa Gateway", "Postal Code": "098269", "Additional Information": "Universal Circle Level 1, outside Garrett's Popcorn"},
    {"Mall Name": "Sengkang Sports Centre", "Address": "57 Anchorvale Rd", "Postal Code": "544964", "Additional Information": "L1 (facing Anchorvale Road)"},
    {"Mall Name": "Sentosa Beach Station", "Address": "50 Beach View", "Postal Code": "098604", "Additional Information": "Opposite Bus Bay 3"},
    {"Mall Name": "Sentosa Cove Village", "Address": "1 Cove Ave, Sentosa Arrival Plaza", "Postal Code": "098537", "Additional Information": "Near Cold Storage Sentosa Cove Village trolley return bay"},
    {"Mall Name": "Tampines Mall", "Address": "4 Tampines Central 5", "Postal Code": "529510", "Additional Information": "L1 Promenade outside Starbucks"},
    {"Mall Name": "Tiong Bahru Market", "Address": "30 Seng Poh Road", "Postal Code": "168898", "Additional Information": "2nd floor of market, near escalators"},
    {"Mall Name": "Westgate", "Address": "3 Gateway Dr", "Postal Code": "608532", "Additional Information": "L1 External Walkway facing JEM"},
    {"Mall Name": "Woodlands Sports Centre", "Address": "1 Woodlands Street 13", "Postal Code": "738597", "Additional Information": "At Stadium Gate 3"},
    {"Mall Name": "Yio Chu Kang Sports Centre", "Address": "200 Ang Mo Kio Ave 9", "Postal Code": "569770", "Additional Information": "At the Squash Courts"}
]

# Function to get latitude and longitude from onemap.sg API
def get_coordinates(postal_code):
    url = f"https://www.onemap.gov.sg/api/common/elastic/search"
    params = {
        "searchVal": postal_code,
        "returnGeom": "Y",
        "getAddrDetails": "N",
        "pageNum": 1
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Check if the API returned results
    if data['found'] > 0:
        latitude = float(data['results'][0]['LATITUDE'])
        longitude = float(data['results'][0]['LONGITUDE'])
        return latitude, longitude
    else:
        print(f"No coordinates found for postal code: {postal_code}")
        return None, None

# Connect to the SQLite database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Insert data into the tables
for mall in mall_data:
    mall_name = mall["Mall Name"]
    address = mall["Address"]
    postal_code = mall["Postal Code"]
    
    # Get latitude and longitude from onemap.sg API
    latitude, longitude = get_coordinates(postal_code)
    
    # Proceed if coordinates were successfully retrieved
    if latitude is not None and longitude is not None:
        try:
            # Insert into Locations table
            cursor.execute("""
                INSERT INTO Locations (Name, "Opening Hours", Address, Latitude, Longitude)
                VALUES (?, 'All Day', ?, ?, ?)
            """, (mall_name, address, latitude, longitude))
            
            # Insert into RecycleCategory table
            cursor.execute("""
                INSERT INTO RecycleCategory (Latitude, Longitude, RecycleItemCategory)
                VALUES (?, ?, 'recyclensave')
            """, (latitude, longitude))
            
            print(f"Inserted {mall_name} into Locations and RecycleCategory tables.")
            
        except sqlite3.IntegrityError:
            print(f"Duplicate entry for {mall_name} with coordinates ({latitude}, {longitude}) – skipping.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            
# Commit the transaction and close the connection
conn.commit()
conn.close()