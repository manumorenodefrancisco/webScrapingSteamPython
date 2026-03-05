import threading
import tkinter as tk
from tkinter import ttk

import main


def llenar_tabla_juegos(tabla, juegos):
    for item in tabla.get_children():
        tabla.delete(item)
    for j in juegos or []:
        tabla.insert("", "end", values=(j.get("id steam"), j.get("titulo"), j.get("precio"), j.get("released"), j.get("fecha_scrap")))

def llenar_tabla_ofertas(tabla, ofertas):
    for item in tabla.get_children():
        tabla.delete(item)
    for o in ofertas or []:
        tabla.insert("", "end", values=(o.get("id steam"), o.get("titulo"), o.get("precio anterior"), o.get("precio actual"), o.get("porcentaje")))


def tarea(inicio, fin, guardar_mongo, root, tbl_juegos, tbl_ofertas, var_texto):
    try:
        juegos, ofertas = main.ejecutar_proceso(inicio, fin, guardar_mongo=guardar_mongo)

        juegos = juegos or []
        ofertas = ofertas or []

        root.after(0, llenar_tabla_juegos, tbl_juegos, juegos)
        root.after(0, llenar_tabla_ofertas, tbl_ofertas, ofertas)
        root.after(0, var_texto.set, f"OK. Juegos: {len(juegos)} | Ofertas: {len(ofertas)}")

    except Exception as e:
        root.after(0, var_texto.set, f"Error: {e}")


def ejecutar_en_hilo(entrada_inicio, entrada_fin, var_mongo, root, tbl_juegos, tbl_ofertas, var_texto):
    var_texto.set("Scrapeando...")
    try:
        inicio = int(entrada_inicio.get())
        fin = int(entrada_fin.get())
    except Exception:
        var_texto.set("Error: páginas no válidas")
        return
    guardar = (var_mongo.get() == 1)
    hilo = threading.Thread(target=tarea, args=(inicio, fin, guardar, root, tbl_juegos, tbl_ofertas, var_texto), daemon=True)
    hilo.start()


def app():
    root = tk.Tk()
    root.title("Steam - Histórico")
    root.geometry("900x600")

    # Top
    frame_top = ttk.Frame(root)
    frame_top.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
    root.columnconfigure(0, weight=1)

    ttk.Label(frame_top, text="Páginas (ini/fin)").grid(row=0, column=0, sticky="w")

    entrada_inicio = ttk.Entry(frame_top, width=5)
    entrada_inicio.insert(0, "1")
    entrada_inicio.grid(row=0, column=1, padx=(5, 8))

    entrada_fin = ttk.Entry(frame_top, width=5)
    entrada_fin.insert(0, "2")
    entrada_fin.grid(row=0, column=2, padx=(0, 8))

    var_mongo = tk.IntVar(value=0)
    ttk.Checkbutton(frame_top, text="Guardar también en Mongo", variable=var_mongo).grid(row=0, column=3, padx=(0, 8))

    var_texto = tk.StringVar(value="Listo")
    ttk.Label(frame_top, textvariable=var_texto).grid(row=0, column=4, sticky="w")

    # Tabs
    contenedor = ttk.Frame(root)
    contenedor.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
    root.rowconfigure(1, weight=1)

    tabs = ttk.Notebook(contenedor)
    tabs.grid(row=0, column=0, sticky="nsew")
    contenedor.columnconfigure(0, weight=1)
    contenedor.rowconfigure(0, weight=1)

    tab_juegos = ttk.Frame(tabs)
    tab_ofertas = ttk.Frame(tabs)
    tabs.add(tab_juegos, text="Juegos")
    tabs.add(tab_ofertas, text="Ofertas")

    # Juegos
    cols_juegos = ("id steam", "titulo", "precio", "released", "fecha")
    tbl_juegos = ttk.Treeview(tab_juegos, columns=cols_juegos, show="headings")
    for columna in cols_juegos:
        tbl_juegos.heading(columna, text=columna)
        tbl_juegos.column(columna, anchor="w")
    tbl_juegos.column("titulo", width=350)
    scroll_juegos = ttk.Scrollbar(tab_juegos, orient="vertical", command=tbl_juegos.yview)
    tbl_juegos.configure(yscrollcommand=scroll_juegos.set)
    tbl_juegos.grid(row=0, column=0, sticky="nsew")
    scroll_juegos.grid(row=0, column=1, sticky="ns")
    tab_juegos.columnconfigure(0, weight=1)
    tab_juegos.rowconfigure(0, weight=1)

    # Ofertas
    cols_ofertas = ("id steam", "titulo", "precio anterior", "precio actual", "%")
    tbl_ofertas = ttk.Treeview(tab_ofertas, columns=cols_ofertas, show="headings")
    for columna in cols_ofertas:
        tbl_ofertas.heading(columna, text=columna)
        tbl_ofertas.column(columna, anchor="w")
    tbl_ofertas.column("titulo", width=350)
    scroll_ofertas = ttk.Scrollbar(tab_ofertas, orient="vertical", command=tbl_ofertas.yview)
    tbl_ofertas.configure(yscrollcommand=scroll_ofertas.set)
    tbl_ofertas.grid(row=0, column=0, sticky="nsew")
    scroll_ofertas.grid(row=0, column=1, sticky="ns")
    tab_ofertas.columnconfigure(0, weight=1)
    tab_ofertas.rowconfigure(0, weight=1)

    boton = ttk.Button(frame_top, text="Scrapear + Guardar", command=lambda: ejecutar_en_hilo(entrada_inicio, entrada_fin, var_mongo, root, tbl_juegos, tbl_ofertas, var_texto))
    boton.grid(row=0, column=5, padx=(8, 0))

    root.mainloop()


if __name__ == "__main__":
    app()