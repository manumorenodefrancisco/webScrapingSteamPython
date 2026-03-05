import openpyxl
import pandas as pandas
import pymongo
import requests
from bs4 import BeautifulSoup
from datetime import datetime

MONGO_CLIENT = "mongodb+srv://manu:manu1231@steam-web-scraper.ryuggsi.mongodb.net/?appName=steam-web-scraper"
ACTUAL_XLSX = "Videojuegos.xlsx"
HIST_XLSX = "JuegosHistorico.xlsx"

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

def ejecutar_proceso(page=1, page_fin=6, guardar_mongo=False):
    arrayJuegos = scrapearJuegos(page, page_fin)

    if not arrayJuegos:
        print("No se scrapearon juegos, devolviendo listas vacías.")
        return [], []

    dataframe_nuevo = pandas.DataFrame(arrayJuegos)
    try:
        dataframe_nuevo["fecha_scrap"] = pandas.to_datetime(dataframe_nuevo["fecha_scrap"])
    except Exception:
        pass

    ofertas = monitor_ofertas(dataframe_nuevo)
    append_excel_historico(dataframe_nuevo)
    upsert_excel_actual(dataframe_nuevo)

    if guardar_mongo:
        guardar_en_mongo(arrayJuegos)

    return arrayJuegos, ofertas

def scrapearJuegos(page=1, page_fin=6):
    arrayJuegos = []
    for page in range(page, page_fin):
        url = BASE_URL + str(page)
        html = sopear(url, page)

        if html:
            juegos = html.find_all("a", class_="search_result_row")

            for juego in juegos:
                dictJuego = {}
                id_steam = juego.get("data-ds-appid")
                titulo = juego.find("span", class_="title").text
                precio = juego.find("div", class_="discount_final_price").text if juego.find("div",
                                                                                             class_="discount_final_price").text != "Free" else "0,00€"
                imagen = juego.find("img").get("src")
                so_nativos = [p.get("class")[1] for p in juego.find_all("span", class_="platform_img")
                              # <span class="platform_img win"></span>
                              if p.get("class")[
                                  1] != "group_separator"]  # <span class="platform_img group_separator"></span> -> no guardar
                released = juego.find("div", class_="search_released").text.strip()
                discount_original_price = juego.find("div",
                                                     class_="discount_original_price").text.strip() if juego.find("div",
                                                                                                                  class_="discount_original_price") else None
                discount_pct = juego.find("div", class_="discount_pct").text if juego.find("div",
                                                                                           class_="discount_pct") else None

                dictJuego["id steam"] = id_steam
                es_vr = True if juego.find("span", class_="vr_supported") else False
                dictJuego["titulo"] = titulo if not es_vr else titulo + "(VR Supported)"
                dictJuego["precio"] = precio[:-1]  # quitar '€'
                if discount_original_price:
                    dictJuego["precio anterior"] = discount_original_price[:-1]
                if discount_pct:
                    dictJuego["porcentaje descuento"] = discount_pct[1:-1]  # -90%
                dictJuego["imagen"] = imagen
                dictJuego["sistemas operativos"] = so_nativos

                dictJuego["released"] = released
                dictJuego["fecha_scrap"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                arrayJuegos.append(dictJuego)

    print(f"Juegos scrapeados: {len(arrayJuegos)}")
    return arrayJuegos

def precio_a_float(txt):
    if txt is None:
        return None
    try:
        texto = str(txt).strip()
        texto = texto.replace("€", "")
        texto = texto.replace(" ", "")
        texto = texto.replace(",", ".")
        return float(texto)
    except Exception:
        return None

def monitor_ofertas(dataframe_nuevo, archivo_historico=HIST_XLSX, porcentaje_minimo=10):
    try:
        datos_historico = pandas.read_excel(archivo_historico, engine='openpyxl')
    except FileNotFoundError:
        print("No hay historico aun.")
        return []

    if datos_historico.empty:
        print("No hay historico aun.")
        return []

    ultimo_precio_por_id = {}
    datos_historico = datos_historico.sort_values("fecha_scrap")
    for indice, fila_historico in datos_historico.iterrows():
        id_steam = fila_historico.get("id steam")
        precio_ant = precio_a_float(fila_historico.get("precio"))
        if id_steam is None:
            continue
        ultimo_precio_por_id[id_steam] = precio_ant

    ofertas = []
    for indice, fila_nueva in dataframe_nuevo.iterrows():
        id_steam = fila_nueva.get("id steam")
        if id_steam is None:
            continue

        precio_ant = ultimo_precio_por_id.get(id_steam)
        precio_act = precio_a_float(fila_nueva.get("precio"))
        if precio_ant is None or precio_act is None:
            continue
        if precio_ant == 0:
            continue

        porcentaje = ((precio_ant - precio_act) / precio_ant) * 100
        if porcentaje >= porcentaje_minimo:
            ofertas.append({
                "id steam": id_steam,
                "titulo": fila_nueva.get("titulo"),
                "precio anterior": precio_ant,
                "precio actual": precio_act,
                "porcentaje": round(porcentaje, 2),
            })

    if ofertas:
        print("OFERTAS (segun tu historico):")
        for oferta in ofertas:
            print(oferta.get("titulo"), "->", oferta.get("precio anterior"), "a", oferta.get("precio actual"), "(", oferta.get("porcentaje"), "%)")
    else:
        print("No hay ofertas segun tu historico.")

    return ofertas

def upsert_excel_actual(dataframe_nuevo, archivo=ACTUAL_XLSX):
    try:
        dataframe_antiguo = pandas.read_excel(archivo, engine='openpyxl')
    except FileNotFoundError:
        dataframe_antiguo = pandas.DataFrame()

    if dataframe_antiguo.empty:
        datos_finales = dataframe_nuevo.copy()
        datos_finales.to_excel(archivo, index=False)
        return datos_finales

    for indice, fila_nueva in dataframe_nuevo.iterrows():
        id_steam = fila_nueva.get("id steam")
        if id_steam is None:
            continue

        filtro_id = dataframe_antiguo["id steam"] == id_steam
        if filtro_id.any():
            for columna in dataframe_nuevo.columns:
                dataframe_antiguo.loc[filtro_id, columna] = fila_nueva.get(columna)
        else:
            dataframe_antiguo = pandas.concat([dataframe_antiguo, fila_nueva.to_frame().T])

    dataframe_antiguo.to_excel(archivo, index=False)
    return dataframe_antiguo

def append_excel_historico(dataframe_nuevo, archivo=HIST_XLSX):
    columnas = ["id steam", "titulo", "precio", "fecha_scrap"]
    if dataframe_nuevo.empty:
        print("DataFrame historico vacío.")
        return
    datos_historico_nuevos = dataframe_nuevo[columnas].copy()

    try:
        datos_historico_antiguos = pandas.read_excel(archivo, engine='openpyxl')
    except FileNotFoundError:
        datos_historico_antiguos = pandas.DataFrame(columns=columnas)

    datos_finales = pandas.concat([datos_historico_antiguos, datos_historico_nuevos])
    datos_finales.to_excel(archivo, index=False)
    return datos_finales

def guardar_en_mongo(juegos_array):
    client = pymongo.MongoClient(MONGO_CLIENT)
    db = client["steam"]
    tabla = db["videojuegos"]

    for i in juegos_array:
        if "id steam" not in i:
            continue
        tabla.update_one({"id steam": i["id steam"]}, {"$set": i}, upsert=True)

    if input("Deseas ver la tabla de mongoDB? (s/n)")=="s":
        for diccionario in tabla.find({}):
            print(diccionario)