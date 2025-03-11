import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import time
import random

def insert_into_database(car_title, car_status, car_specs):
    """Insert car details into MySQL database"""
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="globalautolink"  # Your database name
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
            
            inserted_id = cursor.lastrowid
            
            cursor.close()
            connection.close()
            
            return True, inserted_id
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False, None

def process_car_page(url):
    """Process a single car page and extract details"""
    try:
        print(f"\nProcessing URL: {url}")
        
        # Add a random delay to avoid overloading the server
        delay = random.uniform(1, 3)
        time.sleep(delay)
        
        # Make the request
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch URL: {url}, Status code: {response.status_code}")
            return False
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, "xml")
        
        # Find all items
        items = soup.find_all("div", {'class': 'item'})
        
        if not items:
            print(f"No items found on page: {url}")
            return False
        
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
        
        # Insert into database
        success, car_id = insert_into_database(car_title, car_status, car_specs)
        
        if success:
            print(f"Car details successfully inserted into database with ID: {car_id}")
            print("MySQL connection is closed")
            return True
        else:
            print("Failed to insert car details into database")
            return False
            
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return False

def main():
    # Variables to track progress
    successful_urls = 0
    failed_urls = 0
    total_urls = 0
    
    try:
        # Read all URLs from the file
        with open("car_links.txt", "r") as file:
            urls = [line.strip() for line in file if line.strip()]
            
        total_urls = len(urls)
        print(f"Found {total_urls} URLs in car_links.txt")
        
        # Process each URL
        for i, url in enumerate(urls):
            print(f"\nProcessing URL {i+1}/{total_urls}: {url}")
            
            if process_car_page(url):
                successful_urls += 1
            else:
                failed_urls += 1
        
        # Print summary
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Total URLs: {total_urls}")
        print(f"Successfully processed: {successful_urls}")
        print(f"Failed: {failed_urls}")
        print(f"Success rate: {(successful_urls/total_urls)*100:.2f}%")
        
    except Exception as e:
        print(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()

