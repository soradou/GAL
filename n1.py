import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error

# Open the file in read mode
with open("car_links.txt", "r") as file:
    # Read the first line (which should be the first link)
    first_link = file.readline().strip()

# use the first link
page = requests.get(f"{first_link}")

def insert_into_database(car_title, car_status, car_specs):
    """Insert car details into MySQL database"""
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="globalautolink"  # Replace with your database name
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Prepare the SQL query
            query = """
            INSERT INTO car (title, status, mileage, gearbox, fuel, body_style, doors, int_color, ext_color)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Prepare the values
            values = (
                car_title,
                car_status,
                car_specs.get("Mileage", ""),
                car_specs.get("Gearbox", ""),
                car_specs.get("Fuel", ""),
                car_specs.get("Body Style", ""),
                car_specs.get("Doors", ""),
                car_specs.get("Int Color", ""),
                car_specs.get("Ext Color", "")
            )
            
            # Execute the query
            cursor.execute(query, values)
            connection.commit()
            
            print(f"Car details successfully inserted into database with ID: {cursor.lastrowid}")
            
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

def main(page):
    src = page.content
    soup = BeautifulSoup(src, "xml")
    
    # Find all items
    items = soup.find_all("div", {'class': 'item'})
    
    car_title = "Unknown Car"
    car_status = "Unknown Status"
    car_specs = {}
    
    # First, look for the car title and status
    for item in items:
        price_elem = item.find("span", {"class": "price bigger-pr"})
        if price_elem:
            name_elem = item.find("p", {"class": "item-name"})
            if name_elem:
                car_title = name_elem.text.strip()
                car_status = price_elem.text.strip()
                break
    
    # Then, extract all specifications
    for item in items:
        name_elem = item.find("p", {"class": "item-name"})
        price_elem = item.find("span", {"class": "price"})
        
        if name_elem and price_elem and "bigger-pr" not in price_elem.get("class", []):
            spec_name = name_elem.text.strip()
            spec_value = price_elem.text.strip()
            car_specs[spec_name] = spec_value
    
    # Print car title and status
    print("\n" + "="*50)
    print(f"CAR TITLE: {car_title}")
    print(f"STATUS: {car_status}")
    print("="*50)
    
    # Print specifications
    print("\nCAR SPECIFICATIONS:")
    for spec, value in car_specs.items():
        print(f"{spec}: {value}")
    
    # Insert into database instead of saving to CSV
    insert_into_database(car_title, car_status, car_specs)

main(page)

