import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from mutagen.mp3 import MP3
from PIL import Image, ImageTk, ImageSequence
from ffmpeg import input as ffmpeg_input
from visualizador import VisualizadorFFT

# Método para convertir archivos usanod ffmpeg
def convertirmp3(archivo_mp3, archivo_wav=None):
    if archivo_mp3.lower().endswith((".mp3", ".mpeg")):
        if archivo_wav is None:
            archivo_wav = os.path.splitext(archivo_mp3)[0] + ".wav"
        try:
            ffmpeg_input(archivo_mp3).output(archivo_wav).run(overwrite_output=True, quiet=True)
            return archivo_wav
        except Exception as e:
            messagebox.showerror("Error de conversión", f"No se pudo convertir el archivo: {e}")
            return None
    return archivo_mp3

#Clase con datos de cada canción
class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta_audio):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta_audio = ruta_audio
        self.anterior = None
        self.siguiente = None

# Clase con lista circularDE para guardar y reprodcir las canciones
class ListaReproduccion:
    def __init__(self):
        self.actual = None
    #Método para agregar canción
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
    #Métodos para eliminar una canción
    def eliminar_cancion_actual(self):
        if self.actual is None:
            return
        if self.actual.siguiente == self.actual:
            self.actual = None
        else:
            self.actual.anterior.siguiente = self.actual.siguiente
            self.actual.siguiente.anterior = self.actual.anterior
            self.actual = self.actual.siguiente

    def eliminar_por_indice(self, indice):  
        if self.actual is None:
            return
        temp = self.actual
        for _ in range(indice):
            temp = temp.siguiente
        if temp == self.actual:
            self.eliminar_cancion_actual()
        else:
            temp.anterior.siguiente = temp.siguiente
            temp.siguiente.anterior = temp.anterior

    #Método para vanzar canción
    def avanzar(self):
        if self.actual:
            self.actual = self.actual.siguiente
    #Método para retrceder canción
    def retroceder(self):
        if self.actual:
            self.actual = self.actual.anterior
    #Método para obtener los detalles de cada canción
    def obtener_lista(self):
        canciones = []
        if self.actual is None:
            return canciones
        temp = self.actual
        while True:
            canciones.append(f"{temp.nombre} - {temp.artista} - {temp.duracion}s - {temp.ruta_audio}")
            temp = temp.siguiente
            if temp == self.actual:
                break
        return canciones

#Clase de la interfaz gráfica
class ReproductorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("T   R   O   N   O   S")
        self.root.geometry("1000x600")
        pygame.mixer.init()

        self.lista = ListaReproduccion()
        self.visual = None
        self.en_pausa = False
        self.reproduciendo = False
        #Contenedor principal
        self.contenedor = tk.Frame(self.root, bg="#000000")
        self.contenedor.place(relwidth=1, relheight=1)
        #Barra superior que contiene las opciones para gregar y eliminar canciones
        barra_menu = tk.Menu(self.root, bg="#1F1F1F", fg="#FFFFFF", tearoff=0)
        self.root.config(menu=barra_menu)
        #Boton para agregar canción que se encuentra en la barra superior
        menu_archivo = tk.Menu(barra_menu, tearoff=0, bg="#1F1F1F", fg="#FFFFFF")
        menu_archivo.add_command(label="Cargar canción", command=self.cargar_cancion)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        #Boton para eliminar canción que se encuentra en la barra superior
        menu_control = tk.Menu(barra_menu, tearoff=0)
        menu_control.add_command(label="Eliminar canción seleccionada", command=self.eliminar_seleccionada)
        barra_menu.add_cascade(label="Control", menu=menu_control)

        #Panel principal
        self.panel_principal = tk.Frame(self.contenedor, bg="#000000")
        self.panel_principal.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        #GIF de decoración
        self.gif = Image.open("Craneo.gif")
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((400, 200))) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_actual = 0
        self.label_gif = tk.Label(self.panel_principal, bd=0, highlightthickness=0, bg="#121212")
        self.label_gif.pack(pady=10)
        self.animar_gif()
        #Panel de la izquierda para mostrar las canciones
        self.panel_lista = tk.Frame(self.contenedor, width=300, bg="#111111")
        self.panel_lista.pack(fill=tk.Y, side=tk.LEFT)
        self.panel_lista.pack_propagate(False)
        #Botón para ocultar y mostrar la lista donde se almacenan las canciones
        self.btn_toggle_lista = tk.Button(self.contenedor, text="Ocultar Lista", command=self.MostrarOcultar_lista, bg="#222222", fg="#0ce8ca")
        self.btn_toggle_lista.place(x=10, y=875)

        self.lista_box = tk.Listbox(self.panel_lista, width=40, bg="#1F1F1F", fg="#04e82a")
        self.lista_box.pack(fill=tk.BOTH, expand=True, pady=10)
        #Titulo del programa
        self.titulo_label = tk.Label(self.panel_principal, text="T   R   O   N   O   S", font=("Helvetica", 32, "bold"), bg="#000000", fg="#0ce8ca")
        self.titulo_label.pack(pady=10)
        #Muestra que canción se está reproduciendo
        self.actual_label = tk.Label(self.panel_principal, text="", bg="#000000", fg="#FFFFFF")
        self.actual_label.pack()
        #Se muestra el tiempo que lleva reproduciendo la canción
        self.tiempo_label = tk.Label(self.panel_principal, text="00:00 / 00:00", bg="#000000", fg="#0ce8ca")
        self.tiempo_label.pack()
        #Muestra las barras de frecuencias
        self.visual_frame = tk.Frame(self.panel_principal, bg="#000000")
        self.visual_frame.pack(pady=(5, 5))
        #Muestra la barra de progreso de la canción
        self.progreso = tk.Scale(self.panel_principal, from_=0, to=100, orient=tk.HORIZONTAL, length=600, showvalue=0, state="disabled", bg="#04e82a", troughcolor="#0ce8ca", fg="#0ce8ca", highlightbackground="#121212")
        self.progreso.pack(pady=(5, 5))
        #Muestra los controles para avanzar, retroceder, pausar, reproducir y detener
        self.controles_frame = tk.Frame(self.panel_principal, bg="#121212")
        self.controles_frame.pack()
        #BOTONES PARA CONTROLAR   
        tk.Button(self.controles_frame, text="⏮ Anterior", command=self.anterior, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=0, padx=5)
        tk.Button(self.controles_frame, text="▶ Reproducir", command=self.reproducir, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=1, padx=5)
        tk.Button(self.controles_frame, text="⏸ Pausar", command=self.pausar, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=2, padx=5)
        tk.Button(self.controles_frame, text="⏹ Detener", command=self.detener, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=3, padx=5)
        tk.Button(self.controles_frame, text="⏭ Siguiente", command=self.siguiente, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=4, padx=5)
    #Método para eliminar la canción seleccionada
    def eliminar_seleccionada(self):
        seleccion = self.lista_box.curselection()
        if seleccion:
            indice = seleccion[0]
            self.lista.eliminar_por_indice(indice)
            self.actualizar_lista()
    #Anima el GIF 
    def animar_gif(self):
        frame = self.frames[self.frame_actual]
        self.label_gif.configure(image=frame)
        self.frame_actual = (self.frame_actual + 1) % len(self.frames)
        self.root.after(100, self.animar_gif)
    #Oculta o muestra el panel para mostrar canciones
    def MostrarOcultar_lista(self):
        if self.panel_lista.winfo_ismapped():
            self.panel_lista.pack_forget()
            self.btn_toggle_lista.config(text="Mostrar Lista")
        else:
            self.panel_lista.pack(fill=tk.Y, side=tk.LEFT)
            self.btn_toggle_lista.config(text="Ocultar Lista")
    #Método para que el tiempo se vaya actualizando conforme corre la canción
    def actualizar_tiempo(self):
        if pygame.mixer.music.get_busy():
            tiempo_ms = pygame.mixer.music.get_pos()
            tiempo_seg = tiempo_ms // 1000
            minutos = tiempo_seg // 60
            segundos = tiempo_seg % 60

            duracion = self.lista.actual.duracion
            min_tot = duracion // 60
            seg_tot = duracion % 60

            self.tiempo_label.config(text=f"{minutos:02}:{segundos:02} / {min_tot:02}:{seg_tot:02}")
            self.progreso.config(to=duracion)
            self.progreso.config(state="normal")
            self.progreso.set(tiempo_seg)
            self.progreso.config(state="disabled")

            self.root.after(1000, self.actualizar_tiempo)
        else:
            self.tiempo_label.config(text="00:00 / 00:00")
            self.progreso.set(0)
    #Funcionalidad de botón para agregar canciones
    def cargar_cancion(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.mpeg")])
        if archivo:
            nombre_archivo = os.path.basename(archivo)
            nombre = os.path.splitext(nombre_archivo)[0]
            artista = tk.simpledialog.askstring("Artista", "Nombre del artista:") or "Desconocido"
            duracion = int(MP3(archivo).info.length)

            self.lista.agregar_cancion(nombre, artista, duracion, archivo)
            self.actualizar_lista()
    #Método para actualizar la lista cada vez que se elimina una canción
    def actualizar_lista(self):
        self.lista_box.delete(0, tk.END)
        for cancion in self.lista.obtener_lista():
            self.lista_box.insert(tk.END, cancion)
    #Funcionalidad de botón reproducir 
    def reproducir(self):
        if self.lista.actual:
            if self.en_pausa:
                pygame.mixer.music.unpause()
                self.en_pausa = False
                self.reproduciendo = True
                if self.visual:
                    self.visual.reanudar()
            else:
                pygame.mixer.music.load(self.lista.actual.ruta_audio)
                pygame.mixer.music.play()
                self.en_pausa = False
                self.reproduciendo = True

                self.root.title(f"🎵 Reproduciendo: {self.lista.actual.nombre}")
                self.actual_label.config(text=f"🎶 {self.lista.actual.nombre} - {self.lista.actual.artista}")
                self.actualizar_tiempo()

                if self.visual:
                    self.visual.finalizar()
                    self.visual.canvas.destroy()
                    self.visual = None

                ruta_wav = convertirmp3(self.lista.actual.ruta_audio)
                if ruta_wav:
                    self.visual = VisualizadorFFT(self.visual_frame, ruta_wav, bg="#000000", color="#0ce8ca")
    #Funcionalidad de botón para pausar canción
    def pausar(self):
        if self.reproduciendo and not self.en_pausa:
            pygame.mixer.music.pause()
            self.en_pausa = True
            self.reproduciendo = False
            if self.visual:
                self.visual.pausar()
    #Funcionalidad de botón para detener canción
    def detener(self):
        pygame.mixer.music.stop()
        self.en_pausa = False
        self.reproduciendo = False
        if self.visual:
            self.visual.finalizar()
            self.visual.canvas.destroy()
            self.visual = None
        self.root.title("🎵 Reproductor de Música Simple")
        self.actual_label.config(text="")
    #Funcionalidad de botón para avanzar canción
    def siguiente(self):
        if self.lista.actual:
            self.lista.avanzar()
            self.reproducir()
            self.actualizar_lista()
    #Funcionalidad de botón para retroceder canción
    def anterior(self):
        if self.lista.actual:
            self.lista.retroceder()
            self.reproducir()
            self.actualizar_lista()
    #Funcionalidad de botón para eliminar canción
    def eliminar(self):
        if self.lista.actual:
            self.lista.eliminar_cancion_actual()
            self.detener()
            self.actualizar_lista()


if __name__ == "__main__":
    root = tk.Tk()
    app = ReproductorGUI(root)
    root.mainloop()
