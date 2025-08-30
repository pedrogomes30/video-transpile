import tkinter as tk
from tkinter import filedialog, messagebox
from controller.transcribe_controller import process_video
import os
import subprocess
import platform

input_path = None
status_label = None
transcribe_btn = None
transcription_txt = None
output_dir = None
button_frame = None

# Detecta sistema operacional para abrir arquivos corretamente
def open_file(filepath):
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")

def select_video():
    path = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv")]
    )
    if path:
        input_path.set(path)

def transcribe_video():
    global transcription_txt, output_dir, button_frame

    video_path = input_path.get()
    if not video_path:
        messagebox.showwarning("Aviso", "Selecione um arquivo de vídeo primeiro.")
        return

    try:
        status_label.config(text="Transcrevendo... Aguarde.")
        status_label.update()

        _, blog_txt, hotmart_txt, youtube_txt, output_dir = process_video(video_path)
        transcription_txt = blog_txt  # Principal a ser mostrado no status

        status_label.config(text="Transcrição concluída com sucesso!")

        # Remove botões anteriores (se houver)
        for widget in button_frame.winfo_children():
            widget.destroy()

        # Adiciona novos botões para abrir arquivos
        tk.Label(button_frame, text="Abrir arquivos gerados:", font=("Arial", 10, "bold")).pack(pady=(10, 5))

        tk.Button(button_frame, text="📝 Artigo para Blog", command=lambda: open_file(blog_txt)).pack(pady=2)
        tk.Button(button_frame, text="🎓 Apresentação Hotmart", command=lambda: open_file(hotmart_txt)).pack(pady=2)
        tk.Button(button_frame, text="📺 Descrição para YouTube", command=lambda: open_file(youtube_txt)).pack(pady=2)

    except Exception as e:
        status_label.config(text="Erro na transcrição.")
        messagebox.showerror("Erro", str(e))

def start_app():
    global input_path, status_label, transcribe_btn, button_frame

    window = tk.Tk()
    window.title("Video Transcriber (Whisper)")
    window.geometry("520x400")

    input_path = tk.StringVar()

    tk.Label(window, text="Arquivo de vídeo:").pack(pady=5)
    tk.Entry(window, textvariable=input_path, width=60).pack(pady=5)
    tk.Button(window, text="Selecionar vídeo", command=select_video).pack(pady=5)

    transcribe_btn = tk.Button(window, text="Transcrever vídeo", command=transcribe_video)
    transcribe_btn.pack(pady=10)

    status_label = tk.Label(window, text="", wraplength=500)
    status_label.pack(pady=5)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    window.mainloop()
