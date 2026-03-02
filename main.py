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
        #print(precios)

        for titulo, precio in zip(titulos, precios): # zip une indice de elemnto 1 con indice de elemento 2 (titulos[x] con precios[x])
            texto_precio = precio.text
            if texto_precio == "Free":
                texto_precio = "0,00€"

            dict[titulo.text] = texto_precio[:-1] #para quitarle el €

            print(titulo.text +" - "+ texto_precio)
