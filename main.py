import openpyxl
import pymongo
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

def guardar_en_mongo(juegos):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["steam"]
    tabla = db["videojuegos"]

    for i in juegos:
        if "id steam" not in i:
            continue
        tabla.update_one({"id steam": i["id steam"]}, {"$set": i}, upsert=True)

def mongo_a_excel(archivo="JuegosExcelBD.xlsx"):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["steam"]
    tabla = db["videojuegos"]

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Juegos"

    tablas = ["_id", "id steam", "titulo", "precio", "precio anterior", "porcentaje descuento", "released", "imagen", "sistemas operativos", "fecha_scrap"]
    sheet.append(tablas)

    for diccionario in tabla.find({}):
        so = diccionario.get("sistemas operativos")

        fila = [
            str(diccionario.get("_id")),
            diccionario.get("id steam"),
            diccionario.get("titulo"),
            diccionario.get("precio"),
            diccionario.get("precio anterior"),
            diccionario.get("porcentaje descuento"),
            diccionario.get("released"),
            diccionario.get("imagen"),
            so,
            diccionario.get("fecha_scrap"),
        ]
        sheet.append(fila)

    wb.save(archivo)

arrayJuegos = []
dictJuego = {}
for page in range(1, 3):
    url = BASE_URL + str(page)
    html = sopear(url, page)

    if html:
        juegos = html.find_all("a", class_="search_result_row")

        for juego in juegos:
            dictJuego = {}
            id_steam = juego.get("data-ds-appid")
            titulo = juego.find("span", class_="title").text
            precio = juego.find("div", class_="discount_final_price").text if juego.find("div", class_="discount_final_price").text != "Free" else "0,00€"
            imagen = juego.find("img").get("src")
            so_nativos = [p.get("class")[1] for p in juego.find_all("span", class_="platform_img") # <span class="platform_img win"></span>
                          if p.get("class")[1] != "group_separator"]  # <span class="platform_img group_separator"></span> -> no guardar
            released = juego.find("div", class_="search_released").text.strip()
            discount_original_price = juego.find("div", class_="discount_original_price").text.strip() if juego.find("div", class_="discount_original_price") else None
            discount_pct = juego.find("div", class_="discount_pct").text if juego.find("div", class_="discount_pct") else None

            dictJuego["id steam"] = id_steam
            es_vr = True if juego.find("span", class_="vr_supported") else False
            dictJuego["titulo"] = titulo if not es_vr else titulo + "(VR Supported)"
            dictJuego["precio"] = precio[:-1] # quitar '€'
            if discount_original_price:
                dictJuego["precio anterior"] = discount_original_price[:-1]
            if discount_pct:
                dictJuego["porcentaje descuento"] = discount_pct[1:-1]  # -90%
            dictJuego["imagen"] = imagen
            dictJuego["sistemas operativos"] = so_nativos

            dictJuego["released"] = released
            dictJuego["fecha_scrap"] = "2024-03-04"  # fecha actual

            arrayJuegos.append(dictJuego)
            print(dictJuego)

guardar_en_mongo(arrayJuegos)
ver_mongo(5)
mongo_a_excel()

