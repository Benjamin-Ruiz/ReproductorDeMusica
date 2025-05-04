import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from mutagen.mp3 import MP3
from PIL import Image, ImageTk, ImageSequence
from ffmpeg import input as ffmpeg_input
from visualizador import VisualizadorFFT


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


class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta_audio):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta_audio = ruta_audio
        self.anterior = None
        self.siguiente = None


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

class ReproductorGUI:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#000000")
        self.root.title(" T   R   O   N   O   S")
        self.root.geometry("800x600")
        self.pos_pausa = 0
        self.lista = ListaReproduccion()
        pygame.mixer.init()

        self.visual = None

        
        self.gif = Image.open("Craneo.gif")
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((400, 200))) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_actual = 0
        self.label_gif = tk.Label(root, bd=0, highlightthickness=0, bg="#121212")
        self.label_gif.pack(pady=10)
        self.animar_gif()

        
        barrasuperior = tk.Menu(self.root, bg="#1F1F1F", fg="#FFFFFF", tearoff=0)
        self.root.config(menu=barrasuperior)

        BS_cargar = tk.Menu(barrasuperior, tearoff=0, bg="#1F1F1F", fg="#FFFFFF")
        BS_cargar.add_command(label="Cargar canción", command=self.cargar_cancion)
        barrasuperior.add_cascade(label="Cargar canción", menu=BS_cargar)

        control_menu = tk.Menu(barrasuperior, tearoff=0)
        control_menu.add_command(label="Eliminar canción actual", command=self.eliminar)
        barrasuperior.add_cascade(label="Eliminar canción actual", menu=control_menu)

        # TÍTULO
        self.titulo_label = tk.Label(root, text="T              R              O               N               O               S ", font=("Helvetica", 32, "bold"), bg="#000000", fg="#0ce8ca")
        self.titulo_label.pack(pady=10)

        # LISTA DE CANCIONES
        self.lista_box = tk.Listbox(root, width=100, bg="#000000", fg="#04e82a", selectbackground="#04e82a", selectforeground="#000000")
        self.lista_box.pack(pady=20)

        # TIEMPO
        self.tiempo_label = tk.Label(root, text="00:00 / 00:00", bg="#121212", fg="#0ce8ca")
        self.tiempo_label.pack()

        # VISUALIZADOR
        self.visual_frame = tk.Frame(root, bg="#000000")
        self.visual_frame.pack(pady=(10, 0))

        # SECCION INFERIOR CON PROGRESO Y CONTROLES
        self.seccion_inferior = tk.Frame(root, bg="#000000")
        self.seccion_inferior.pack(side=tk.BOTTOM, pady=10)

        self.progreso = tk.Scale(self.seccion_inferior, from_=0, to=100, orient=tk.HORIZONTAL, length=600,
                                 showvalue=0, state="disabled", bg="#04e82a", troughcolor="#0ce8ca",
                                 fg="#0ce8ca", highlightbackground="#121212")
        self.progreso.pack(pady=(0, 5))

        self.controles_frame = tk.Frame(self.seccion_inferior, bg="#121212")
        self.controles_frame.pack()

        tk.Button(self.controles_frame, text="⏮ Anterior", command=self.anterior, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=0, padx=5)
        tk.Button(self.controles_frame, text="▶ Reproducir", command=self.reproducir, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=2, padx=5)
        tk.Button(self.controles_frame, text="⏸ Pausar", command=self.pausar, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=4, padx=5)
        tk.Button(self.controles_frame, text="⏹ Detener", command=self.detener, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=6, padx=5)
        tk.Button(self.controles_frame, text="⏭ Siguiente", command=self.siguiente, bg="#1F1F1F", fg="#0ce8ca").grid(row=0, column=8, padx=5)

    def animar_gif(self):
        frame = self.frames[self.frame_actual]
        self.label_gif.configure(image=frame)
        self.frame_actual = (self.frame_actual + 1) % len(self.frames)
        self.root.after(100, self.animar_gif)

    def actualizar_tiempo(self):
        if pygame.mixer.music.get_busy():
            tiempoms = pygame.mixer.music.get_pos()
            tiemposeg = tiempoms // 1000
            minutos = tiemposeg // 60
            segundos = tiemposeg % 60

            duracionTotal = self.lista.actual.duracion
            minTotales = duracionTotal // 60
            segTotales = duracionTotal % 60

            self.tiempo_label.config(text=f"{minutos:02}:{segundos:02} / {minTotales:02}:{segTotales:02}")

            self.progreso.config(to=duracionTotal)
            self.progreso.config(state="normal")
            self.progreso.set(tiemposeg)
            self.progreso.config(state="disabled")

            self.root.after(1000, self.actualizar_tiempo)
        else:
            self.tiempo_label.config(text="00:00 / 00:00")
            self.progreso.config(state="normal")
            self.progreso.set(0)
            self.progreso.config(state="disabled")

    def cargar_cancion(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.mpeg")])
        if archivo:
            nombre_archivo = os.path.basename(archivo)
            nombre = os.path.splitext(nombre_archivo)[0]
            artista = "Desconocido"

            audio = MP3(archivo)
            duracion = int(audio.info.length)

            self.lista.agregar_cancion(nombre, artista, duracion, archivo)
            self.actualizar_lista()

    def actualizar_lista(self):
        self.lista_box.delete(0, tk.END)
        for cancion in self.lista.obtener_lista():
            self.lista_box.insert(tk.END, cancion)

    def reproducir(self):
        if self.lista.actual:
            if not pygame.mixer.music.get_busy() and self.pos_pausa > 0:
                pygame.mixer.music.unpause()
                if self.visual:
                    self.visual.reanudar()
            else:
                # Empezar canción desde 0
                pygame.mixer.music.stop()
                self.pos_pausa = 0
                if self.visual:
                    self.visual.finalizar()
                    self.visual.canvas.destroy()
                    self.visual = None

                pygame.mixer.music.load(self.lista.actual.ruta_audio)
                pygame.mixer.music.play()
                self.root.title(f"🎵 Reproduciendo: {self.lista.actual.nombre}")
                self.actualizar_tiempo()

                ruta_wav = convertirmp3(self.lista.actual.ruta_audio)
                if ruta_wav:
                    self.visual = VisualizadorFFT(self.visual_frame, ruta_wav, bg="#000000", color="#0ce8ca")

    def pausar(self):
        if pygame.mixer.music.get_busy():
            self.pos_pausa = pygame.mixer.music.get_pos() / 1000 
            pygame.mixer.music.pause()
            if self.visual:
                self.visual.pausar()


    def detener(self):
        pygame.mixer.music.stop()
        if self.visual:
            self.visual.finalizar()
            self.visual.canvas.destroy()
            self.visual = None
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


