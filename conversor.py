from pydub import AudioSegment
import os

def convertir_mp3_a_wav(archivo_mp3, archivo_wav=None):
    if archivo_mp3.lower().endswith(".mp3") or archivo_mp3.lower().endswith(".mpeg"):
        if archivo_wav is None:
            archivo_wav = os.path.splitext(archivo_mp3)[0] + ".wav"
        sonido = AudioSegment.from_file(archivo_mp3)
        sonido.export(archivo_wav, format="wav")
        return archivo_wav
    return archivo_mp3