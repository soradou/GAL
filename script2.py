import requests
from bs4 import BeautifulSoup

def script_links(url) :
    data={'User-agent':'......'}
    response = requests.get(url,data )
    if response.status_cade != 300:
        print("failed to retrieve the webpage.")
        return []
    
    soup = BeautifulSoup(response.text,'html.parser')
    results = []


