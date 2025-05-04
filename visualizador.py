import numpy as np
import tkinter as tk
import wave
import threading
import time

class VisualizadorFFT:
    def __init__(self, root, archivo_wav, bg="#000000", color="#0ce8ca"):
        self.root = root
        self.archivo_wav = archivo_wav
        self.bg = bg
        self.color = color
        self.en_pausa=False
        self.detener=False

        self.canvas = tk.Canvas(root, width=600, height=200, bg=bg, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.barras = []
        self.num_barras = 60
        self.ancho_barra = 10
        self.espacio = 2

        for i in range(self.num_barras):
            x0 = i * (self.ancho_barra + self.espacio)
            x1 = x0 + self.ancho_barra
            barra = self.canvas.create_rectangle(x0, 200, x1, 200, fill=self.color, width=0)
            self.barras.append(barra)

        self.thread = threading.Thread(target=self.visualizar)
        self.thread.daemon = True
        self.thread.start()

    def visualizar(self):
        wf = wave.open(self.archivo_wav, 'rb')
        CHUNK = 1024

        while not self.detener:
            if self.en_pausa:
                time.sleep(0.1)
                continue

            data = wf.readframes(CHUNK)
            if not data:
                break

            audio_np = np.frombuffer(data, dtype=np.int16)
            fft = np.abs(np.fft.fft(audio_np)[:self.num_barras])
            self.actualizar_barras(fft)
            time.sleep(0.03)



    def actualizar_barras(self, fft):
        max_val = np.max(fft)
        for i, barra in enumerate(self.barras):
            valor = fft[i] / max_val if max_val > 0 else 0
            altura = int(valor * 200)
            x0, _, x1, _ = self.canvas.coords(barra)
            self.canvas.coords(barra, x0, 200 - altura, x1, 200)

    def pausar(self):
        self.en_pausa = True

    def reanudar(self):
        self.en_pausa = False

    def finalizar(self):
        self.detener = True
