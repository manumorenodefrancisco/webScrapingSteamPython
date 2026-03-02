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
            id_steam = juego.get("data-ds-appid")
            titulo = juego.find("span", class_="title").text
            precio = juego.find("div", class_="discount_final_price").text if precio.text != "Free" else precio.text = "0,00€"
            imagen = juego.find("img").text
            so_nativos = [p.get("class")[1] for p in juego.find_all("span", class_="platform_img") # <span class="platform_img win"></span>
                          if p.get("class")[1] != "group_separator"]  # <span class="platform_img group_separator"></span> -> no guardar
            released = juego.find("div", class_="search_released").text.strip()
            discount_original_price = juego.find("div", class_="discount_original_price").text.strip()
            discount_pct = juego.find("div", class_="discount_pct").text

            dictJuego["id steam"] = id_steam
            es_vr = True if juego.find("span", class_="vr_supported") else False
            dictJuego["titulo"] = titulo if not es_vr else titulo + "(VR Supported)"
            dictJuego["precio"] = precio[:-1] # quitar '€'
            dictJuego["precio anterior"] = discount_original_price[:-1] #no siempre hay
            dictJuego["porcentaje descuento"] = discount_pct[1:-1]  # -90%, no siempre hay
            dictJuego["imagen"] = imagen
            dictJuego["sistemas operativos"] = so_nativos

            dictJuego["released"] = released

            arrayJuegos.append(dictJuego)
            print(arrayJuegos)

