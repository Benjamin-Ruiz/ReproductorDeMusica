import tkinter as tk
import random

class VisualizadorFalso:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador TRONOS")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, width=600, height=200, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.barras = []
        self.num_barras = 30
        self.ancho_barra = 15
        self.espacio = 5

        for i in range(self.num_barras):
            x0 = i * (self.ancho_barra + self.espacio)
            x1 = x0 + self.ancho_barra
            barra = self.canvas.create_rectangle(x0, 200, x1, 200, fill="#0ce8ca", width=0)
            self.barras.append(barra)

        self.animar()

    def animar(self):
        for i, barra in enumerate(self.barras):
            altura = random.randint(10, 200)
            x0, _, x1, _ = self.canvas.coords(barra)
            self.canvas.coords(barra, x0, 200 - altura, x1, 200)
        self.root.after(100, self.animar)




