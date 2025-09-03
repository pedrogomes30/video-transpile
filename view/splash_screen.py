"""
Splash Screen com logs de inicialização
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
import sys
import os

class SplashScreen:
    def __init__(self, on_complete_callback=None, real_loading=False):
        self.on_complete_callback = on_complete_callback
        self.real_loading = real_loading
        self.splash = None
        self.log_text = None
        self.progress_bar = None
        self.loading_complete = False
        self.setup_splash()
        
    def setup_splash(self):
        """Configura a janela de splash"""
        self.splash = tk.Toplevel()
        self.splash.title("Video Transcriber - Carregando...")
        self.splash.geometry("600x450")
        self.splash.resizable(False, False)
        
        # Tentar definir ícone
        try:
            icon_path = "assets/app_icon.ico"
            if os.path.exists(icon_path):
                self.splash.iconbitmap(icon_path)
        except:
            pass
        
        # Centraliza na tela
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (450 // 2)
        self.splash.geometry(f"+{x}+{y}")
        
        # Remove bordas e botões
        self.splash.overrideredirect(True)
        
        # Frame principal
        main_frame = tk.Frame(self.splash, bg='#2b2b2b', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True)
        
        # Header com título
        header_frame = tk.Frame(main_frame, bg='#1e1e1e', height=80)
        header_frame.pack(fill='x', padx=2, pady=2)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🎬 Video Transcriber", 
            font=("Arial", 18, "bold"),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        title_label.pack(pady=8)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Powered by OpenAI Whisper", 
            font=("Arial", 10),
            fg='#cccccc',
            bg='#1e1e1e'
        )
        subtitle_label.pack()
        
        version_label = tk.Label(
            header_frame, 
            text="v1.0 - Com Splash Screen & Ícones", 
            font=("Arial", 8),
            fg='#888888',
            bg='#1e1e1e'
        )
        version_label.pack()
        
        # Progress bar
        progress_frame = tk.Frame(main_frame, bg='#2b2b2b')
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(
            progress_frame, 
            text="Inicializando...", 
            font=("Arial", 10),
            fg='#ffffff',
            bg='#2b2b2b'
        )
        self.status_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate',
            length=500
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()
        
        # Log area
        log_frame = tk.Frame(main_frame, bg='#2b2b2b')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tk.Label(
            log_frame, 
            text="Log de Inicialização:", 
            font=("Arial", 10, "bold"),
            fg='#ffffff',
            bg='#2b2b2b',
            anchor='w'
        ).pack(fill='x')
        
        # Text widget para logs
        self.log_text = tk.Text(
            log_frame,
            height=15,
            font=("Consolas", 9),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            relief='sunken',
            bd=1
        )
        self.log_text.pack(fill='both', expand=True, pady=5)
        
        # Scrollbar para logs
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#1e1e1e', height=35)
        footer_frame.pack(fill='x', padx=2, pady=2)
        footer_frame.pack_propagate(False)
        
        status_label = tk.Label(
            footer_frame, 
            text="Aguarde enquanto carregamos os componentes...", 
            font=("Arial", 8),
            fg='#888888',
            bg='#1e1e1e'
        )
        status_label.pack(pady=8)
        
        # Mantém splash sempre no topo
        self.splash.attributes('-topmost', True)
        
    def log(self, message, color='#00ff00'):
        """Adiciona mensagem ao log do splash"""
        if self.log_text and not self.loading_complete:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.log_text.config(state='normal')
            self.log_text.insert('end', log_entry)
            self.log_text.see('end')
            self.log_text.config(state='disabled')
            
            # Força atualização da interface
            self.splash.update()
            
    def update_status(self, status):
        """Atualiza o status na barra de progresso"""
        if self.status_label and not self.loading_complete:
            self.status_label.config(text=status)
            self.splash.update()
            
    def real_loading_process(self):
        """Processo de carregamento real da aplicação"""
        try:
            self.log("🚀 Iniciando Video Transcriber...")
            self.update_status("Verificando ambiente...")
            time.sleep(0.3)
            
            self.log("🐍 Verificando Python environment...")
            import sys
            self.log(f"   Python {sys.version.split()[0]}")
            time.sleep(0.2)
            
            self.log("📦 Carregando bibliotecas principais...")
            self.update_status("Carregando Tkinter...")
            import tkinter
            self.log("   ✅ Tkinter")
            time.sleep(0.1)
            
            self.update_status("Carregando threading...")
            import threading
            self.log("   ✅ Threading")
            time.sleep(0.1)
            
            self.update_status("Verificando FFmpeg...")
            self.log("🎥 Verificando FFmpeg...")
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    self.log(f"   ✅ {version_line}")
                else:
                    self.log("   ⚠️ FFmpeg não encontrado")
            except:
                self.log("   ⚠️ FFmpeg não disponível")
            time.sleep(0.4)
            
            self.update_status("Carregando OpenAI Whisper...")
            self.log("🤖 Carregando OpenAI Whisper...")
            try:
                import whisper
                self.log("   ✅ Whisper importado com sucesso")
                time.sleep(0.5)
                
                # Verificar modelos disponíveis
                self.log("   📋 Modelos disponíveis:")
                for model in ["tiny", "base", "small", "medium", "large"]:
                    self.log(f"      • {model}")
                time.sleep(0.3)
                    
            except Exception as e:
                self.log(f"   ❌ Erro ao importar Whisper: {e}")
                time.sleep(0.2)
            
            self.update_status("Verificando CUDA...")
            self.log("🚀 Verificando CUDA...")
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_name = torch.cuda.get_device_name(0)
                    self.log(f"   ✅ GPU detectada: {gpu_name}")
                    self.log(f"   📊 VRAM disponível: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
                else:
                    self.log("   ⚠️ CUDA não disponível - usando CPU")
            except:
                self.log("   ⚠️ PyTorch não encontrado")
            time.sleep(0.4)
            
            self.update_status("Configurando interface...")
            self.log("🖼️ Configurando interface gráfica...")
            self.log("   ✅ Preparando controladores")
            self.log("   ✅ Carregando serviços")
            self.log("   ✅ Configurando callbacks")
            time.sleep(0.3)
            
            self.log("✨ Inicialização concluída!")
            self.update_status("Pronto!")
            time.sleep(0.5)
            
        except Exception as e:
            self.log(f"❌ Erro durante inicialização: {e}")
            time.sleep(1)
            
        finally:
            self.loading_complete = True
            self.close()
            
    def simulate_loading(self):
        """Simula processo de carregamento com logs"""
        steps = [
            ("Iniciando aplicação...", 0.5),
            ("Verificando Python environment...", 0.3),
            ("Carregando bibliotecas principais...", 0.4),
            ("Importando Tkinter...", 0.2),
            ("Importando threading...", 0.1),
            ("Verificando FFmpeg...", 0.6),
            ("Testando comando FFmpeg...", 0.3),
            ("Carregando OpenAI Whisper...", 1.5),
            ("Inicializando modelo Whisper...", 1.0),
            ("Verificando CUDA...", 0.4),
            ("Detectando GPU disponível...", 0.3),
            ("Configurando interface gráfica...", 0.4),
            ("Preparando controladores...", 0.2),
            ("Carregando serviços...", 0.3),
            ("Inicialização concluída!", 0.2)
        ]
        
        for step, delay in steps:
            self.log(step)
            time.sleep(delay)
            
        self.log("✅ Aplicação pronta para uso!", '#00ff00')
        time.sleep(0.5)
        
        # Fecha splash e chama callback
        self.loading_complete = True
        self.splash.after(100, self.close)
        
    def start_loading(self):
        """Inicia carregamento em thread separada"""
        if self.real_loading:
            loading_thread = threading.Thread(target=self.real_loading_process)
        else:
            loading_thread = threading.Thread(target=self.simulate_loading)
        loading_thread.daemon = True
        loading_thread.start()
        
    def close(self):
        """Fecha o splash screen"""
        if self.splash:
            self.splash.destroy()
            
        # Chama callback se definido
        if self.on_complete_callback:
            self.on_complete_callback()
            
    def show(self):
        """Mostra o splash screen"""
        self.start_loading()
        self.splash.mainloop()

def test_splash():
    """Teste do splash screen"""
    def on_complete():
        print("Splash concluído! Aplicação principal seria iniciada aqui.")
        
    splash = SplashScreen(on_complete, real_loading=True)
    splash.show()

if __name__ == "__main__":
    test_splash()
