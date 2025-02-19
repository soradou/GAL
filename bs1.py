import requests
from bs4 import BeautifulSoup
import csv

page = requests.get("https://caroutlet.es/fr/toutes-nos-voitures/?carproducer=0&car_price_min=&car_price_max=&car_year_from=2022&car_year_to=2024&car_mileage_from=&car_mileage_to=&car_fuel_type=0&car_transmission=0")

def main(page):
    src = page.content 
    print(src)

main(page)