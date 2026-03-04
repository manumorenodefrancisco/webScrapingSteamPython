import tkinter as tk
from tkinter import END, Text, Spinbox, Toplevel, Scale, HORIZONTAL  # import *

#1
root = tk.Tk()
root.title("Saludos")
#root.geometry("400x300")
#2
tk.Label(root, text="Nombre").grid(row=0, column=0) # o etiqueta.pack()
tk.Label(root, text="Apellidos").grid(row=1, column=0)
tk.Entry(root).grid(row=0, column=1)
tk.Entry(root).grid(row=1, column=1)
#3
var1 = tk.IntVar()#1 o 0
var2 = tk.IntVar()
tk.Checkbutton(root, text="Mesi", variable=var1).grid(row=3, sticky="w")# o sticky=tk.W o si es sin grid: pack(side=tk.LEFT)
tk.Checkbutton(root, text="Cr7", variable=var2).grid(row=4, sticky="w")
#4
v = tk.IntVar()
tk.Radiobutton(root, text="A", variable=v, value=1).grid(row=5, sticky="w")
tk.Radiobutton(root, text="B", variable=v, value=2).grid(row=6, sticky="w")
#5
lb = tk.Listbox(root)
lb.insert(1, "Python")
lb.insert(2, "Java")
lb.insert(3, "C++")
lb.insert(4, "Any other")
lb.grid(row=7, column=0, columnspan=2)
#6
text_widget = Text(root, height=2, width=30)
text_widget.insert(END, "Frase de varias\nlineas jeje\n")
text_widget.grid(row=9, column=0)
#7
spinbox = Spinbox(root, from_=0, to=10)
spinbox.grid(row=10, column=0)
#8
scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=8, column=0)

mylist = tk.Listbox(root, yscrollcommand=scrollbar.set)#-> connects the listbox to the scrollbar.

for line in range(100):
    mylist.insert(tk.END, "This is line number " + str(line))

mylist.grid(row=8, column=0, columnspan=1)
scrollbar.config(command=mylist.yview)# Enables scrolling behavior
#9
menu = tk.Menu(root)
root.config(menu=menu)

filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)#-> adds dropdown menus
filemenu.add_command(label="New")
filemenu.add_command(label="Open...")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)

helpmenu = tk.Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About")
#10
top = Toplevel()# (abrir ventana vacia)
top.title('Python')
#11
vertical_scale = Scale(root, from_=0, to=42)
vertical_scale.grid(row=11, column=0)
horizontal_scale = Scale(root, from_=0, to=200, orient="horizontal")
horizontal_scale.grid(row=11, column=1)
#12 y 13 -> Faltan MenuButton y Progressbar

#14
boton = tk.Button(root, text="Cerrar", width=25, command=root.destroy)
boton.grid(row=12, column=1, columnspan=2, pady=10)

root.mainloop()