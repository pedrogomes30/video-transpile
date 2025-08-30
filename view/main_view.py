import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from controller.transcribe_controller import process_video
from service.whisper_service import play_notification_sound
import os
import subprocess
import platform
import threading
import sys
import gc
from datetime import datetime

# Constantes para ícones e aparência
ICON_PATH = "assets/app_icon.ico"
APP_TITLE = "🎬 Video Transcriber (Whisper) - Com Log de Debug"
APP_GEOMETRY = "750x650"

input_path = None
status_label = None
transcribe_btn = None
transcription_txt = None
output_dir = None
button_frame = None
progress_bar = None
progress_label = None
log_text = None

# Variáveis para controle de processos
current_thread = None
is_processing = False

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

def log_message(message):
    """Adiciona uma mensagem ao log com timestamp"""
    global log_text
    if log_text:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_text.config(state='normal')
        log_text.insert('end', f"[{timestamp}] {message}\n")
        log_text.see('end')
        log_text.config(state='disabled')
        log_text.update()

def setup_window_icon(window):
    """Configura o ícone da janela"""
    try:
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
            log_message(f"✅ Ícone carregado: {ICON_PATH}")
        else:
            log_message(f"⚠️ Ícone não encontrado: {ICON_PATH}")
    except Exception as e:
        log_message(f"❌ Erro ao carregar ícone: {e}")

def clear_log():
    """Limpa o log"""
    global log_text
    if log_text:
        log_text.config(state='normal')
        log_text.delete(1.0, 'end')
        log_text.config(state='disabled')

def on_closing(window):
    """Função chamada quando a janela é fechada"""
    global current_thread, is_processing
    
    if is_processing:
        # Pergunta ao usuário se quer realmente fechar durante processamento
        result = messagebox.askyesno(
            "Fechar Aplicação", 
            "Há um processamento em andamento.\n\n"
            "Fechar agora pode deixar processos em execução.\n\n"
            "Deseja realmente fechar?"
        )
        
        if not result:
            return  # Cancela o fechamento
    
    try:
        log_message("Encerrando aplicação...")
        
        # Para thread de processamento se existir
        if current_thread and current_thread.is_alive():
            log_message("Aguardando thread de processamento...")
            # Nota: threading em Python não permite kill forçado
            # Mas definimos is_processing=False para sinalizar parada
            is_processing = False
        
        # Força limpeza de memória
        gc.collect()
        
        # Importa torch se disponível e limpa cache
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                log_message("Cache CUDA limpo")
        except:
            pass
        
        log_message("Aplicação encerrada")
        
    except Exception as e:
        print(f"Erro ao encerrar: {e}")
    
    finally:
        # Força encerramento da aplicação
        window.quit()
        window.destroy()
        sys.exit(0)

def select_video():
    path = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv")]
    )
    if path:
        input_path.set(path)

def update_progress(percentage):
    """Atualiza a barra de progresso e o label"""
    progress_bar['value'] = percentage
    progress_label.config(text=f"Processando... {percentage}%")
    progress_bar.update()

def transcribe_video_thread():
    """Função que roda a transcrição em thread separada"""
    global transcription_txt, output_dir, button_frame

    video_path = input_path.get()
    
    try:
        log_message("=== INICIANDO TRANSCRIÇÃO ===")
        log_message(f"Arquivo de vídeo: {video_path}")
        
        # Mostra barra de progresso
        progress_bar.pack(pady=5)
        progress_label.pack(pady=2)
        
        log_message("Verificando dependências...")
        
        # Teste de importação das principais bibliotrias
        try:
            import torch
            log_message(f"✓ PyTorch carregado: {torch.__version__}")
            log_message(f"✓ CUDA disponível: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                log_message(f"✓ GPU: {torch.cuda.get_device_name(0)}")
        except Exception as e:
            log_message(f"✗ Erro ao carregar PyTorch: {e}")
            
        try:
            import whisper
            log_message("✓ Whisper carregado")
        except Exception as e:
            log_message(f"✗ Erro ao carregar Whisper: {e}")
            
        try:
            import ffmpeg
            log_message("✓ FFmpeg carregado")
        except Exception as e:
            log_message(f"✗ Erro ao carregar FFmpeg: {e}")
        
        log_message("Iniciando processamento do vídeo...")
        
        def progress_callback(percentage):
            update_progress(percentage)
            log_message(f"Progresso: {percentage}%")
        
        _, blog_txt, hotmart_txt, youtube_txt, output_dir = process_video(video_path, progress_callback, log_message)
        transcription_txt = blog_txt

        # Esconde barra de progresso
        progress_bar.pack_forget()
        progress_label.pack_forget()
        
        log_message("=== TRANSCRIÇÃO CONCLUÍDA ===")
        log_message(f"Arquivos gerados em: {output_dir}")
        log_message(f"- Blog: {blog_txt}")
        log_message(f"- Hotmart: {hotmart_txt}")
        log_message(f"- YouTube: {youtube_txt}")
        
        status_label.config(text="Transcrição concluída com sucesso!")

        # Remove botões anteriores (se houver)
        for widget in button_frame.winfo_children():
            widget.destroy()

        # Adiciona novos botões para abrir arquivos
        tk.Label(button_frame, text="Abrir arquivos gerados:", font=("Arial", 10, "bold")).pack(pady=(10, 5))

        tk.Button(button_frame, text="📝 Artigo para Blog", command=lambda: open_file(blog_txt)).pack(pady=2)
        tk.Button(button_frame, text="🎓 Apresentação Hotmart", command=lambda: open_file(hotmart_txt)).pack(pady=2)
        tk.Button(button_frame, text="📺 Descrição para YouTube", command=lambda: open_file(youtube_txt)).pack(pady=2)

        # Reabilita botão de transcrever
        transcribe_btn.config(state="normal")

    except Exception as e:
        # Esconde barra de progresso em caso de erro
        progress_bar.pack_forget()
        progress_label.pack_forget()
        
        log_message(f"✗ ERRO NA TRANSCRIÇÃO: {str(e)}")
        log_message(f"Tipo do erro: {type(e).__name__}")
        
        # Log do stack trace completo
        import traceback
        stack_trace = traceback.format_exc()
        log_message("Stack trace completo:")
        for line in stack_trace.split('\n'):
            if line.strip():
                log_message(f"  {line}")
        
        # Toca som de erro
        play_notification_sound("alert")
        
        status_label.config(text="Erro na transcrição.")
        messagebox.showerror("Erro", str(e))
        transcribe_btn.config(state="normal")

def transcribe_video():
    global transcription_txt, output_dir, button_frame

    video_path = input_path.get()
    if not video_path:
        messagebox.showwarning("Aviso", "Selecione um arquivo de vídeo primeiro.")
        return

    # Limpa o log anterior
    clear_log()
    log_message("Sistema iniciado")
    log_message(f"Python: {sys.version}")
    log_message(f"Plataforma: {platform.system()} {platform.release()}")

    # Verifica se há GPU disponível antes de transcrever
    try:
        from service.whisper_service import is_gpu_available
        gpu_available = is_gpu_available()
        log_message(f"GPU disponível: {gpu_available}")
        
        if not gpu_available:
            log_message("Nenhuma GPU detectada, perguntando ao usuário...")
            proceed = messagebox.askyesno(
                "Atenção: Sem GPU detectada",
                "Não foi detectada uma GPU NVIDIA disponível. Prosseguir pela CPU? (Pode demorar MUITO mais tempo)"
            )
            if not proceed:
                log_message("Transcrição cancelada pelo usuário")
                status_label.config(text="Transcrição cancelada pelo usuário.")
                return
            else:
                log_message("Usuario optou por continuar com CPU")
        
        status_label.config(text="Iniciando transcrição...")
        status_label.update()
        
        # Desabilita botão durante processamento
        transcribe_btn.config(state="disabled")
        
        # Inicia transcrição em thread separada
        thread = threading.Thread(target=transcribe_video_thread)
        thread.daemon = True
        thread.start()

    except Exception as e:
        log_message(f"Erro ao verificar GPU: {e}")
        status_label.config(text="Erro na transcrição.")
        messagebox.showerror("Erro", str(e))

def start_app():
    global input_path, status_label, transcribe_btn, button_frame, progress_bar, progress_label, log_text

    log_message("🚀 Iniciando interface principal...")
    
    window = tk.Tk()
    window.title(APP_TITLE)
    window.geometry(APP_GEOMETRY)
    
    # Configura ícone da aplicação
    setup_window_icon(window)
    
    # Configura ação de fechamento da janela
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))

    input_path = tk.StringVar()

    # Frame superior para controles
    top_frame = tk.Frame(window)
    top_frame.pack(pady=10, padx=10, fill='x')

    tk.Label(top_frame, text="Arquivo de vídeo:").pack(pady=5)
    tk.Entry(top_frame, textvariable=input_path, width=60).pack(pady=5)
    # Botão para selecionar vídeo
    select_btn = tk.Button(
        top_frame, 
        text="📁 Selecionar Vídeo", 
        command=select_video,
        font=("Arial", 10),
        bg='#4CAF50',
        fg='white',
        relief='raised',
        bd=2
    )
    select_btn.pack(pady=5)

    # Botão para transcrever
    transcribe_btn = tk.Button(
        top_frame, 
        text="🚀 Transcrever Vídeo", 
        command=transcribe_video,
        font=("Arial", 10, "bold"),
        bg='#2196F3',
        fg='white',
        relief='raised',
        bd=2
    )
    transcribe_btn.pack(pady=10)

    status_label = tk.Label(top_frame, text="", wraplength=500)
    status_label.pack(pady=5)

    # Barra de progresso (inicialmente oculta)
    progress_bar = ttk.Progressbar(top_frame, length=400, mode='determinate')
    progress_label = tk.Label(top_frame, text="")

    button_frame = tk.Frame(top_frame)
    button_frame.pack(pady=10)

    # Frame para o log
    log_frame = tk.Frame(window)
    log_frame.pack(pady=10, padx=10, fill='both', expand=True)

    tk.Label(log_frame, text="Log de Processamento:", font=("Arial", 10, "bold")).pack(anchor='w')
    
    # Área de texto com scroll para o log
    log_text = scrolledtext.ScrolledText(
        log_frame, 
        height=15, 
        width=80, 
        state='disabled',
        font=("Consolas", 9),
        bg="black",
        fg="lightgreen"
    )
    log_text.pack(fill='both', expand=True, pady=5)

    # Botão para limpar log
    # Botão para limpar log
    clear_btn = tk.Button(
        log_frame, 
        text="🗑️ Limpar Log", 
        command=clear_log,
        font=("Arial", 9),
        bg='#FF5722',
        fg='white',
        relief='raised',
        bd=1
    )
    clear_btn.pack(pady=5)

    # Log inicial
    log_message("Aplicação iniciada - Aguardando seleção de vídeo")

    window.mainloop()
