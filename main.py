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


arrayJuegos = []
dictJuego = {}
for page in range(1, 3):
    url = BASE_URL + str(page)
    html = sopear(url, page)

    if html:
        juegos = html.find_all("a", class_="search_result_row")

        for juego in juegos:
            titulo = juego.find("span", class_="title")
            precio = juego.find("div", class_="discount_final_price")
            imagen = juego.find("img")
            released = juego.find("div", class_="search_released")
            plataformas = [p.get("class")[1] if p.get("class")[1] != "group_separator" else juego.find("span", class_="vr_supported").text
                           for p in juego.find_all("span", class_="platform_img")] # <span class="platform_img win"></span>
            # <span class="platform_img group_separator"></span> -> no guardar
            # <span class="vr_supported">Compatible con la RV</span>

            texto_precio = precio.text
            if texto_precio == "Free":
                texto_precio = "0,00€"
            # print(titulo.text +" - "+ texto_precio)

            dictJuego["titulo"] = titulo.text
            dictJuego["precio"] = texto_precio[:-1] # para quitarle el €
            dictJuego["imagen"] = imagen.text
            dictJuego["plataformas"] = plataformas
            dictJuego["released"] = released.text.strip()

            arrayJuegos.append(dictJuego)
            print(arrayJuegos)