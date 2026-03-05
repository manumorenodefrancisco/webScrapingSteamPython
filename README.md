# webScrapingSteamPython
Monitor Simple de Ofertas Gaming


Sistema que:

Scrapea recorriendo juegos en Instant Gaming/Steam con bucle, usando requests y BeautifulSoup y con paginación.

Guarda su precio en excel con pandas y en mongo

Cuando vuelves a comprobar: Compara precio anterior vs nuevo. Si baja → lo marca como oferta

Guarda también los datos en Excel (hay que usar openpyxl)

Interfaz simple con Tkinter


Web scraping en python con requests y beautifulSoap con bbdd en excel usando openpyxl y sqlite, en todos los juegos de la sección Tendencias de Steam con paginacion recorriendo de juego en juego y guardando sus datos.
id (interno, INTEGER PK)
nombre
url
precio_actual
precio_anterior
ultima_revision (TEXT (fecha))

id (INTEGER PK)
videojuego_id (FK)
precio
fecha


El Excel será una copia espejo de la base de datos sincronizada con ella, usando openpyxl, con copia de seguridad y con:
Hoja 1 → Videojuegos
Hoja 2 → Historial




MongoDB Atlas es MongoDB en la nube (como Firebase, pero para Mongo). No instalas nada en tu PC, solo te conectas a internet.
