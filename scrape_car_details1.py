import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from car_ad import CarAd
import requests
import mysql.connector
from mysql.connector import Error


# Set paths manually
CHROME_PATH = "C:\\seleniumChromeDriver\\chrome-win64\\chrome.exe"  # Path to Chrome
CHROMEDRIVER_PATH = "C:\\seleniumChromeDriver\\chromedriver-win64\\chromedriver.exe"  # Path to ChromeDriver

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.binary_location = CHROME_PATH  # Specify Chrome path
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
# MySQL Database Connection
db = mysql.connector.connect(host="localhost", user="root", password="", database="globalautolink")
cursor = db.cursor()
  

def scrape_car_details(url):
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load
    
    def get_text(by, value, default="Not Available"):
        try:
            return driver.find_element(by, value).text.strip()
        except:
            return default
    
    def extract_brand_model(title):
        parts = title.split(" - ")
        brand = parts[0].split()[0] if parts else "Not Available"
        model = parts[0].split()[1] if len(parts[0].split()) > 1 else "Not Available"
        return brand, model
    
    def extract_numeric(value):
        return "".join(filter(str.isdigit, value)) if value != "Not Available" else "0"
    
    def extract_country(country_text):
        return country_text.split("/")[0].strip() if country_text != "Not Available" else "Not Available"
    
    title_text = get_text(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/form/div/h3[1]")
    car_brand, car_model = extract_brand_model(title_text)
  
    energy = get_text(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/form/div/div[3]/span")
    if "diesel" in energy.lower():
        energy = "Diesel"
    elif "petrol" in energy.lower():
        energy = "Petrol"
    elif "hybrid" in energy.lower():
        energy = "Hybrid"
    else:
        energy = "Petrol"

    carType = get_text(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/form/div/div[4]/span")
    if "suv" in carType.lower():
        carType = "SUV"
    elif "hatchback" in carType.lower():
        carType = "Hatchback"
    elif "sedan" in carType.lower():
        carType = "Sedan"
    else:
        carType = "Sedan"

    image_elements = driver.find_elements(By.XPATH, "/html/body/div[2]/div[3]/div[1]/div[1]/div/ul/li/a/img")

    print(" length of images is ", len(image_elements))
    image_urls = [img.get_attribute("src") for img in image_elements]

    car_ad=CarAd(
        title=title_text,
        original_pub_date="Not Available",
        original_url=url,
        local_url="url",
        scraped_date=time.strftime("%Y-%m-%d %H:%M:%S"),
        carBrand=car_brand,
        carModel=car_model,
        year=get_text(By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/div[6]/div", "0"),
        currentMiles=extract_numeric(get_text(By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/div[1]/div", "0")),
        carType=carType,
        energy=energy,
        country=extract_country(get_text(By.XPATH, "/html/body/div[2]/div[1]/div[1]/div")),  
        price=extract_numeric(get_text(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/form/div/div[13]/span")),
        gearbox=get_text(By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/div[3]/div"),
        wd="Not Available",  # No clear info on page
        is_available=1  # Assuming car is available if listed
    )

    return car_ad, image_urls


def download_images(image_urls, carads_id):
        os.makedirs("uploads", exist_ok=True)
        image_paths = []
        for idx, img_url in enumerate(image_urls):
            image_name = f"car_{carads_id}_{idx}.jpg"
            image_path = os.path.join("C:/Users/Dell/Desktop/GAL/uploads", image_name)
            try:
                img_data = requests.get(img_url, stream=True).content
                with open(image_path, "wb") as img_file:
                    img_file.write(img_data)


                sql = """
                INSERT INTO caradsimages (carads_id, image_title, image_url) 
                VALUES (%s, %s, %s)
                """
                values = (carads_id, image_name, f"/uploads/{image_name}")
                cursor.execute(sql, values)
                db.commit()


                image_paths.append((carads_id, image_name, image_path))
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
        return image_paths


# Read URLs from car_links.txt file
def read_car_links(file_path="car_links.txt"):
    with open(file_path, 'r') as file:
        # Read all lines and strip whitespace
        return [line.strip() for line in file if line.strip()]

# Main execution
try:
    # Get all car URLs from the file
    car_urls = read_car_links()
    print(f"Found {len(car_urls)} car URLs to process")
    
    # Process each URL
    for index, car_url in enumerate(car_urls):
        try:
            print(f"\nProcessing car {index+1}/{len(car_urls)}: {car_url}")
            
            # Scrape car details
            car_details, images = scrape_car_details(car_url)
            
            # Insert into database
            car_details.insert_into_db(host="localhost", user="root", password="", database="globalautolink")
            print(f"Inserted into database with ID: {car_details.get_id}")
            
            # Download and save images
            if images:
                print(f"Downloading {len(images)} images...")
                image_records = download_images(images, car_details.get_id())
                print(f"Downloaded {len(image_records)} images successfully")
            else:
                print("No images found for this car")
                
            # Optional: Add a delay between requests to avoid overloading the server
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing URL {car_url}: {e}")
            # Continue with the next URL even if this one fails
            continue
            
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Always close the driver and database connection
    print("Closing WebDriver and database connection")
    driver.quit()
    if db.is_connected():
        cursor.close()
        db.close()
        print("Database connection closed")