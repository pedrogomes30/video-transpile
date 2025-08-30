import tkinter as tk
from view.splash_screen import SplashScreen
from view.main_view import start_app

def launch_app():
    """Inicia a aplicação com splash screen"""
    def on_splash_complete():
        # Inicia a aplicação principal após splash
        start_app()
    
    # Criar e mostrar splash screen com carregamento real
    splash = SplashScreen(on_splash_complete, real_loading=True)
    splash.show()

if __name__ == "__main__":
    launch_app()
