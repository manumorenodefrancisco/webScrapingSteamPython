import requests
from bs4 import BeautifulSoup

BASE_URL = "https://store.steampowered.com/search/?page="

headers = {
    "User-Agent": "Mozilla/5.0"
}

def sopear(url, page):
    response = requests.get(url, headers=headers, verify=False)

    print(f"PÁGINA {page} → STATUS: {response.status_code}")

    if response.status_code != 200:
        print("Bloqueo detectado.")
        return None

    return BeautifulSoup(response.content, "html.parser")

dict = {}
for page in range(1, 3):
    url = BASE_URL + str(page)
    html = sopear(url, page)

    if html:
        titulos = html.find_all("span", class_="title")
        precios = html.find_all("div", class_="discount_final_price")
        print(titulos)
        print(precios)

