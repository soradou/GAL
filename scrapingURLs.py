import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Set paths manually
CHROME_PATH = "C:\\seleniumChromeDriver\\chrome-win64\\chrome.exe"  # Path to Chrome
CHROMEDRIVER_PATH = "C:\\seleniumChromeDriver\\chromedriver-win64\\chromedriver.exe"  # Path to ChromeDriver

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.binary_location = CHROME_PATH  # Specify Chrome path
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Set the ChromeDriver service with the correct path
service = Service(CHROMEDRIVER_PATH)

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ ChromeDriver launched successfully!")

    url = "https://caroutlet.es/all-our-cars/?carproducer=0&car_price_min=&car_price_max=&car_year_from=2015&car_year_to=2025"
    driver.get(url)

    # Initialize scrolling logic
    car_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to bottom
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)  # Wait for new content to load

        # Extract car links
        car_elements = driver.find_elements(By.CLASS_NAME, "button-detail")
        for car in car_elements:
            href = car.get_attribute("href")
            if href:
                car_links.add(href)

        # Check if we have reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📌 No more new articles to load. Stopping...")
            break
        last_height = new_height

    print(f"✅ Total Cars Found: {len(car_links)}")

    # Save links to a text file in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script location
    save_path = os.path.join(script_dir, "car_links.txt")  # Save file in the same folder

    with open(save_path, "w") as file:
        for link in car_links:
            if "all-our-cars" not in link:
                file.write(link + "\n")

    print(f"📂 Links saved at: {save_path}")

except Exception as e:
    print("❌ An error occurred:", str(e))

finally:
    driver.quit()  # Close the browser
    print("🛑 ChromeDriver session closed.")
