import tkinter as tk
from tkinter import filedialog, messagebox
from controller.transcribe_controller import process_video
import os

input_path = None
status_label = None
transcribe_btn = None
transcription_txt = None
output_dir = None

def select_video():
    path = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv")]
    )
    if path:
        input_path.set(path)

def transcribe_video():
    global transcription_txt, output_dir
    video_path = input_path.get()
    if not video_path:
        messagebox.showwarning("Aviso", "Selecione um arquivo de vídeo primeiro.")
        return

    try:
        status_label.config(text="Transcrevendo... Aguarde.")
        status_label.update()
        _, transcription_txt, output_dir = process_video(video_path)
        status_label.config(text=f"Transcrição salva em:\n{transcription_txt}")
    except Exception as e:
        status_label.config(text="Erro na transcrição.")
        messagebox.showerror("Erro", str(e))

def start_app():
    global input_path, status_label, transcribe_btn

    window = tk.Tk()
    window.title("Video Transcriber (Whisper)")
    window.geometry("500x250")

    input_path = tk.StringVar()

    tk.Label(window, text="Arquivo de vídeo:").pack(pady=5)
    tk.Entry(window, textvariable=input_path, width=60).pack(pady=5)
    tk.Button(window, text="Selecionar vídeo", command=select_video).pack(pady=5)

    transcribe_btn = tk.Button(window, text="Transcrever vídeo", command=transcribe_video)
    transcribe_btn.pack(pady=10)

    status_label = tk.Label(window, text="")
    status_label.pack()

    window.mainloop()