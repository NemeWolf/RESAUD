from tkinter import Text, Button, Tk

ventana = Tk()

# Crea la ventana de texto
ventana_texto = Text(ventana)

# Crea el cuadro de entrada
cuadro_entrada = input(ventana)

# Crea el botón
boton = Button(ventana, text="Insertar texto")

# Asigna el manejador de eventos al botón
boton.bind("<Button-1>", "insertar_texto")

# Muestra la ventana de texto
ventana_texto.pack()

# Muestra el cuadro de entrada
cuadro_entrada.pack()

# Muestra el botón
boton.pack()

def insertar_texto():
  # Lee el texto del cuadro de entrada
  texto = cuadro_entrada.get()

  # Inserta el texto en la ventana de texto
  ventana_texto.insert("1.0", texto)

ventana.mainloop()