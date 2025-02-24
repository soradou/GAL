import requests
from bs4 import BeautifulSoup
import csv

Y1 = input("Please enter a year in the following format Y1: ")
Y2 = input("Please enter a year in the following format Y2: ")
page = requests.get(f"https://caroutlet.es/fr/toutes-nos-voitures/?carproducer=0&car_price_min=&car_price_max=&car_year_from={Y1}&car_year_to={Y2}")

def main(page):
    src = page.content
    soup = BeautifulSoup(src, "lxml")

    # Fix: Iterate over the list of elements to access 'href'
    cars = [car['href'] for car in soup.find_all("a", {'class': 'button-detail'}) if 'href' in car.attrs]
    print("S2!:", cars)

    if cars:  # Check if there are any cars found
        p2 = requests.get(cars[0])  # Using the first link as an example
        s2 = BeautifulSoup(p2.content, "lxml")
        car = s2.find_all("div", {'class': 'item'})
        print("data:", car)
    else:
        print("No car links found!")

main(page)
