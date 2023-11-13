from tkinter import Button, Tk

ventana = Tk()

def cambiar_estado(estado):
  button.config(state=estado)

button = Button(ventana, text="Cambiar estado", command=lambda: cambiar_estado("normal"))
button.pack()

ventana.mainloop()

