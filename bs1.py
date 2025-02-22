import requests
from bs4 import BeautifulSoup
import csv
Y1 = input ("Please enter a year in the following format Y1 : ")
Y2 = input ("Please enter a year in the following format Y2 :")
page = requests.get(f"https://caroutlet.es/fr/toutes-nos-voitures/?carproducer=0&car_price_min=&car_price_max=&car_year_from={Y1}&car_year_to={Y2}&car_mileage_from=&car_mileage_to=&car_fuel_type=0&car_transmission=0")

def main(page):
    src = page.content 
    soup = BeautifulSoup(src, "lxml")
    cars = soup.find_all("div", {'class': 'article-car'})
    print(cars)
    
main(page)