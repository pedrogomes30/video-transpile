#!/usr/bin/env python3
"""
Script de teste e diagnóstico para o Video Transcriber.
"""

import os
import sys
import platform
import subprocess
import importlib.util

def test_header():
    """Exibe cabeçalho do teste."""
    print("🎬 Video Transcriber - Diagnóstico do Sistema")
    print("=" * 50)
    print(f"🖥️ Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 50)

def test_python_packages():
    """Testa se os pacotes Python estão instalados."""
    print("\n📦 TESTE DE PACOTES PYTHON")
    print("-" * 30)
    
    required_packages = {
        "whisper": "openai-whisper",
        "cv2": "opencv-python", 
        "moviepy": "moviepy",
        "transformers": "transformers",
        "tkinter": "tkinter (built-in)"
    }
    
    all_ok = True
    
    for import_name, package_name in required_packages.items():
        try:
            if import_name == "tkinter":
                import tkinter
            else:
                __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name} - ERRO: {e}")
            all_ok = False
    
    return all_ok

def test_ffmpeg():
    """Testa se o FFmpeg está funcionando."""
    print("\n🎬 TESTE DO FFMPEG")
    print("-" * 20)
    
    # Verifica no PATH
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg no PATH: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ FFmpeg não encontrado no PATH")
    
    # Verifica no diretório local (Windows)
    if platform.system() == "Windows":
        if os.path.exists("ffmpeg.exe"):
            try:
                result = subprocess.run(["./ffmpeg.exe", "-version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    print(f"✅ FFmpeg local: {version_line}")
                    return True
            except subprocess.TimeoutExpired:
                print("❌ FFmpeg local não responde")
        else:
            print("❌ ffmpeg.exe não encontrado no diretório")
    
    return False

def test_whisper_model():
    """Testa se o modelo Whisper pode ser carregado."""
    print("\n🤖 TESTE DO MODELO WHISPER")
    print("-" * 25)
    
    try:
        import whisper
        print("🔄 Carregando modelo 'small'...")
        model = whisper.load_model("small")
        print("✅ Modelo carregado com sucesso!")
        
        # Limpa a memória
        del model
        import gc
        gc.collect()
        
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False

def test_gui():
    """Testa se a interface gráfica pode ser inicializada."""
    print("\n🖥️ TESTE DA INTERFACE GRÁFICA")
    print("-" * 30)
    
    try:
        import tkinter as tk
        
        # Cria uma janela de teste
        root = tk.Tk()
        root.withdraw()  # Esconde a janela
        
        # Testa componentes básicos
        tk.Label(root, text="Teste")
        tk.Button(root, text="Teste")
        tk.Entry(root)
        
        root.destroy()
        
        print("✅ Interface gráfica funcional!")
        return True
    except Exception as e:
        print(f"❌ Erro na interface gráfica: {e}")
        return False

def test_file_permissions():
    """Testa permissões de escrita."""
    print("\n📁 TESTE DE PERMISSÕES")
    print("-" * 20)
    
    try:
        # Testa criação de diretório
        test_dir = "output/test"
        os.makedirs(test_dir, exist_ok=True)
        print("✅ Criação de diretórios: OK")
        
        # Testa criação de arquivo
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Teste de escrita")
        print("✅ Criação de arquivos: OK")
        
        # Limpa arquivos de teste
        os.remove(test_file)
        os.rmdir(test_dir)
        print("✅ Remoção de arquivos: OK")
        
        return True
    except Exception as e:
        print(f"❌ Erro de permissões: {e}")
        return False

def test_video_formats():
    """Lista formatos de vídeo suportados."""
    print("\n🎥 FORMATOS DE VÍDEO SUPORTADOS")
    print("-" * 32)
    
    formats = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"]
    
    for fmt in formats:
        print(f"✅ {fmt}")
    
    print("\n💡 Recomendado: .mp4 para melhor compatibilidade")

def generate_report(results):
    """Gera relatório final."""
    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL DO DIAGNÓSTICO")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"📊 Testes realizados: {total_tests}")
    print(f"✅ Testes aprovados: {passed_tests}")
    print(f"❌ Testes falharam: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("   O Video Transcriber está pronto para uso.")
    elif passed_tests >= total_tests - 1:
        print("\n⚠️ SISTEMA QUASE PRONTO")
        print("   Corrija os problemas menores antes de usar.")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS")
        print("   Vários componentes precisam ser corrigidos.")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    if not results.get("packages", False):
        print("   1. Instale os pacotes Python: pip install -r requirements.txt")
    if not results.get("ffmpeg", False):
        print("   2. Configure o FFmpeg: python setup_ffmpeg.py")
    if not results.get("whisper", False):
        print("   3. Verifique a conexão com internet para download do modelo")
    if not results.get("gui", False):
        print("   4. Instale as dependências da GUI (tkinter)")
    if not results.get("permissions", False):
        print("   5. Verifique as permissões de escrita no diretório")
    
    if passed_tests == total_tests:
        print("   ▶️ Execute: python app.py")

def main():
    """Função principal."""
    test_header()
    
    # Executa todos os testes
    tests = {
        "packages": test_python_packages,
        "ffmpeg": test_ffmpeg,
        "whisper": test_whisper_model,
        "gui": test_gui,
        "permissions": test_file_permissions,
    }
    
    results = {}
    
    for test_name, test_function in tests.items():
        try:
            results[test_name] = test_function()
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {e}")
            results[test_name] = False
    
    # Informações adicionais
    test_video_formats()
    
    # Relatório final
    generate_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Diagnóstico cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico durante o diagnóstico: {e}")
        sys.exit(1)
