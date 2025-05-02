import pygame
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# Nodo para las canciones
class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta_audio):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta_audio = ruta_audio
        self.anterior = None
        self.siguiente = None
#Nodo para la lista 
class NodoListas():
    def __init__(self, NombreLista):
        self.NombreLita=NombreLista
        self.primero=None
        self.actual=None

#Lista de reproducción
class Listas():
    def __init__(self):
        self.actual=None

class ListaReproduccion:
    def __init__(self):
        self.actual = None

    def agregar_cancion(self, nombre, artista, duracion, ruta_audio):
        nueva = NodoCancion(nombre, artista, duracion, ruta_audio)
        if self.actual is None:
            nueva.siguiente = nueva
            nueva.anterior = nueva
            self.actual = nueva
        else:
            ultimo = self.actual.anterior
            nueva.siguiente = self.actual
            nueva.anterior = ultimo
            ultimo.siguiente = nueva
            self.actual.anterior = nueva

    def eliminar_cancion_actual(self):
        if self.actual is None:
            return
        if self.actual.siguiente == self.actual:
            self.actual = None
        else:
            self.actual.anterior.siguiente = self.actual.siguiente
            self.actual.siguiente.anterior = self.actual.anterior
            self.actual = self.actual.siguiente

    def avanzar(self):
        if self.actual:
            self.actual = self.actual.siguiente

    def retroceder(self):
        if self.actual:
            self.actual = self.actual.anterior

    def obtener_lista(self):
        canciones = []
        if self.actual is None:
            return canciones
        temp = self.actual
        while True:
            canciones.append(f"{temp.nombre} - {temp.artista}")
            temp = temp.siguiente
            if temp == self.actual:
                break
        return canciones


# Interfaz 
class ReproductorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(" T   R   O   N   O   S")
        self.root.geometry("500x400")
        self.lista = ListaReproduccion()
        pygame.mixer.init()

        # Botones

        barrasuperior=tk.Menu(self.root)
        self.root.config(menu=barrasuperior)

        BS_cargar=tk.Menu(barrasuperior,tearoff=0)
        BS_cargar.add_command(label="Cargar canción",command=self.cargar_cancion)
        BS_cargar.add_cascade(label="Archivo", menu=BS_cargar)

        self.lista_box = tk.Listbox(root, width=50)
        self.lista_box.pack(pady=10)

        self.btn_cargar = tk.Button(root, text="Cargar canción", command=self.cargar_cancion)
        self.btn_cargar.pack()

        self.controles_frame = tk.Frame(root)
        self.controles_frame.pack(pady=10)

        tk.Button(self.controles_frame, text="⏮ Anterior", command=self.anterior).grid(row=0, column=0, padx=5)
        tk.Button(self.controles_frame, text="▶ Reproducir", command=self.reproducir).grid(row=0, column=1, padx=5)
        tk.Button(self.controles_frame, text="⏸ Pausar", command=self.pausar).grid(row=0, column=2, padx=5)
        tk.Button(self.controles_frame, text="⏹ Detener", command=self.detener).grid(row=0, column=3, padx=5)
        tk.Button(self.controles_frame, text="⏭ Siguiente", command=self.siguiente).grid(row=0, column=4, padx=5)

    def cargar_cancion(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.mpeg" )])
        if archivo:
            nombre_archivo = os.path.basename(archivo)
            nombre = os.path.splitext(nombre_archivo)[0]
            artista = "Desconocido"
            duracion = 30  

            self.lista.agregar_cancion(nombre, artista, duracion, archivo)
            self.actualizar_lista()

    def actualizar_lista(self):
        self.lista_box.delete(0, tk.END)
        for cancion in self.lista.obtener_lista():
            self.lista_box.insert(tk.END, cancion)

    def reproducir(self):
        if self.lista.actual:
            pygame.mixer.music.load(self.lista.actual.ruta_audio)
            pygame.mixer.music.play()
            self.root.title(f"🎵 Reproduciendo: {self.lista.actual.nombre}")

    def pausar(self):
        pygame.mixer.music.pause()

    def detener(self):
        pygame.mixer.music.stop()
        self.root.title("🎵 Reproductor de Música Simple")

    def siguiente(self):
        if self.lista.actual:
            self.lista.avanzar()
            self.reproducir()
            self.actualizar_lista()

    def anterior(self):
        if self.lista.actual:
            self.lista.retroceder()
            self.reproducir()
            self.actualizar_lista()

    def eliminar(self):
        if self.lista.actual:
            self.lista.eliminar_cancion_actual()
            self.detener()
            self.actualizar_lista()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReproductorGUI(root)
    root.mainloop()

