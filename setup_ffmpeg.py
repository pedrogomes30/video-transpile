#!/usr/bin/env python3
"""
Script para baixar e configurar o FFmpeg automaticamente.
"""

import os
import platform
import requests
import zipfile
import shutil
import subprocess
from pathlib import Path

def download_file(url, filename):
    """Download de arquivo com barra de progresso."""
    print(f"📥 Baixando {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r📊 Progresso: {percent:.1f}%", end='', flush=True)
    
    print(f"\n✅ {filename} baixado com sucesso!")

def setup_ffmpeg_windows():
    """Configura FFmpeg no Windows."""
    print("🪟 Configurando FFmpeg para Windows...")
    
    # URL do FFmpeg para Windows
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Baixa o FFmpeg
    zip_filename = "ffmpeg-windows.zip"
    download_file(ffmpeg_url, zip_filename)
    
    # Extrai o arquivo
    print("📂 Extraindo FFmpeg...")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall("temp_ffmpeg")
    
    # Move o executável para o diretório do projeto
    ffmpeg_dir = None
    for root, dirs, files in os.walk("temp_ffmpeg"):
        if "ffmpeg.exe" in files:
            ffmpeg_dir = root
            break
    
    if ffmpeg_dir:
        shutil.copy(os.path.join(ffmpeg_dir, "ffmpeg.exe"), "ffmpeg.exe")
        print("✅ FFmpeg instalado com sucesso!")
    else:
        print("❌ Erro: ffmpeg.exe não encontrado no arquivo baixado")
        return False
    
    # Limpa arquivos temporários
    shutil.rmtree("temp_ffmpeg", ignore_errors=True)
    os.remove(zip_filename)
    
    return True

def setup_ffmpeg_linux():
    """Configura FFmpeg no Linux."""
    print("🐧 Configurando FFmpeg para Linux...")
    
    try:
        # Tenta instalar via apt
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
        print("✅ FFmpeg instalado via apt!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar FFmpeg via apt")
        return False

def setup_ffmpeg_macos():
    """Configura FFmpeg no macOS."""
    print("🍎 Configurando FFmpeg para macOS...")
    
    try:
        # Tenta instalar via brew
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        print("✅ FFmpeg instalado via Homebrew!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar FFmpeg via Homebrew")
        print("💡 Instale o Homebrew primeiro: https://brew.sh/")
        return False

def test_ffmpeg():
    """Testa se o FFmpeg está funcionando."""
    print("🧪 Testando FFmpeg...")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg está funcionando corretamente!")
            return True
        else:
            print("❌ FFmpeg não está respondendo corretamente")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg não encontrado no PATH")
        return False

def main():
    """Função principal."""
    print("🎬 Configurador Automático do FFmpeg")
    print("=" * 40)
    
    system = platform.system()
    
    if system == "Windows":
        success = setup_ffmpeg_windows()
    elif system == "Linux":
        success = setup_ffmpeg_linux()
    elif system == "Darwin":  # macOS
        success = setup_ffmpeg_macos()
    else:
        print(f"❌ Sistema operacional não suportado: {system}")
        return False
    
    if success:
        test_ffmpeg()
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Instalação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante a instalação: {e}")
