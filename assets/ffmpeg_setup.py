"""
Download e configuração do FFmpeg para distribuição
"""

import os
import sys
import zipfile
import urllib.request
import subprocess
import shutil
from pathlib import Path

def download_ffmpeg_windows():
    """Baixa FFmpeg para Windows"""
    ffmpeg_dir = Path("assets/ffmpeg")
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    
    # URLs para download do FFmpeg (usando versão mais recente)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ffmpeg_zip = ffmpeg_dir / "ffmpeg.zip"
    
    print("📥 Baixando FFmpeg...")
    
    try:
        # Download do arquivo
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
        print(f"✅ FFmpeg baixado: {ffmpeg_zip}")
        
        # Extrair o arquivo
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Encontrar o executável
        for root, dirs, files in os.walk(ffmpeg_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = Path(root) / "ffmpeg.exe"
                # Copiar para assets/ffmpeg/
                shutil.copy2(ffmpeg_exe, ffmpeg_dir / "ffmpeg.exe")
                print(f"✅ FFmpeg copiado para: {ffmpeg_dir / 'ffmpeg.exe'}")
                break
        
        # Limpar arquivo zip
        ffmpeg_zip.unlink()
        
        # Limpar diretórios extras
        for item in ffmpeg_dir.iterdir():
            if item.is_dir() and item.name.startswith("ffmpeg-"):
                shutil.rmtree(item)
                
        return ffmpeg_dir / "ffmpeg.exe"
        
    except Exception as e:
        print(f"❌ Erro ao baixar FFmpeg: {e}")
        
        # Tentar URL alternativo
        try:
            print("🔄 Tentando URL alternativo...")
            alt_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            urllib.request.urlretrieve(alt_url, ffmpeg_zip)
            print(f"✅ FFmpeg baixado (alternativo): {ffmpeg_zip}")
            
            # Extrair o arquivo
            with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
            
            # Encontrar o executável
            for root, dirs, files in os.walk(ffmpeg_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_exe = Path(root) / "ffmpeg.exe"
                    # Copiar para assets/ffmpeg/
                    shutil.copy2(ffmpeg_exe, ffmpeg_dir / "ffmpeg.exe")
                    print(f"✅ FFmpeg copiado para: {ffmpeg_dir / 'ffmpeg.exe'}")
                    break
            
            # Limpar arquivo zip
            ffmpeg_zip.unlink()
            
            # Limpar diretórios extras
            for item in ffmpeg_dir.iterdir():
                if item.is_dir() and item.name.startswith("ffmpeg-"):
                    shutil.rmtree(item)
                    
            return ffmpeg_dir / "ffmpeg.exe"
            
        except Exception as e2:
            print(f"❌ Erro no URL alternativo: {e2}")
            return None

def check_ffmpeg_embedded():
    """Verifica se FFmpeg está disponível no diretório da aplicação"""
    possible_paths = [
        "assets/ffmpeg/ffmpeg.exe",
        "ffmpeg/ffmpeg.exe", 
        "ffmpeg.exe",
        "./ffmpeg.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
    
    return None

def setup_ffmpeg_for_build():
    """Configura FFmpeg para inclusão no build"""
    print("🔧 Configurando FFmpeg para build...")
    
    # Verificar se já existe
    existing_ffmpeg = check_ffmpeg_embedded()
    if existing_ffmpeg:
        print(f"✅ FFmpeg já disponível: {existing_ffmpeg}")
        return existing_ffmpeg
    
    # Baixar se necessário
    if sys.platform == "win32":
        ffmpeg_path = download_ffmpeg_windows()
        if ffmpeg_path and ffmpeg_path.exists():
            return str(ffmpeg_path)
    
    print("❌ Não foi possível configurar FFmpeg")
    return None

def test_ffmpeg(ffmpeg_path):
    """Testa se FFmpeg está funcionando"""
    try:
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg testado com sucesso: {version_line}")
            return True
        else:
            print(f"❌ FFmpeg retornou erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar FFmpeg: {e}")
        return False

if __name__ == "__main__":
    print("🎥 Configurador de FFmpeg")
    print("=" * 40)
    
    ffmpeg_path = setup_ffmpeg_for_build()
    if ffmpeg_path:
        if test_ffmpeg(ffmpeg_path):
            print(f"\n✅ FFmpeg pronto para build: {ffmpeg_path}")
        else:
            print(f"\n❌ FFmpeg configurado mas com problemas: {ffmpeg_path}")
    else:
        print("\n❌ Falha na configuração do FFmpeg")
        print("\nSoluções alternativas:")
        print("1. Instale FFmpeg manualmente no sistema")
        print("2. Adicione FFmpeg ao PATH")
        print("3. Copie ffmpeg.exe para assets/ffmpeg/")
