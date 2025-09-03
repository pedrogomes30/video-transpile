#!/usr/bin/env python3
"""
Script automatizado para build do Video Transcriber.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"⚡ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}:")
        print(f"   Código de retorno: {e.returncode}")
        print(f"   Saída: {e.stdout}")
        print(f"   Erro: {e.stderr}")
        return False

def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    print("🔍 Verificando dependências...")
    
    required_packages = ["pyinstaller", "whisper", "opencv-python"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} encontrado")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} não encontrado")
    
    if missing_packages:
        print(f"\n📦 Instalando pacotes faltantes: {', '.join(missing_packages)}")
        install_cmd = f"{sys.executable} -m pip install {' '.join(missing_packages)}"
        return run_command(install_cmd, "Instalação de dependências")
    
    return True

def prepare_ffmpeg():
    """Prepara o FFmpeg para o build."""
    print("🎬 Preparando FFmpeg...")
    
    system = platform.system()
    
    if system == "Windows":
        # Verifica se ffmpeg.exe existe no diretório atual
        if not os.path.exists("ffmpeg.exe"):
            print("⚠️ ffmpeg.exe não encontrado. Executando setup automático...")
            if not run_command(f"{sys.executable} setup_ffmpeg.py", "Setup do FFmpeg"):
                return False
        else:
            print("✅ ffmpeg.exe encontrado!")
    
    else:
        # Linux/macOS - verifica se está no PATH
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            print("✅ FFmpeg encontrado no sistema!")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ FFmpeg não encontrado. Executando setup automático...")
            if not run_command(f"{sys.executable} setup_ffmpeg.py", "Setup do FFmpeg"):
                return False
    
    return True

def clean_build():
    """Limpa arquivos de build anteriores."""
    print("🧹 Limpando builds anteriores...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["app.spec", "*.pyc"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ Removido: {dir_name}/")
    
    # Remove arquivos específicos
    for file_pattern in files_to_clean:
        if "*" in file_pattern:
            import glob
            for file in glob.glob(file_pattern):
                os.remove(file)
                print(f"🗑️ Removido: {file}")
        else:
            if os.path.exists(file_pattern):
                os.remove(file_pattern)
                print(f"🗑️ Removido: {file_pattern}")
    
    # Remove __pycache__ recursivamente
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)
                print(f"🗑️ Removido: {os.path.join(root, dir_name)}/")

    print("✅ Limpeza concluída!")

def get_build_config():
    """Obtém configurações de build personalizadas."""
    config = {
        "app_name": "VideoTranscriber",
        "console_mode": False,
        "debug_mode": False,
        "icon_path": None,
        "upx_compression": True,
        "exclude_modules": [
            'matplotlib',
            'pandas', 
            'numpy.distutils',
            'scipy',
            'pytest',
            'setuptools',
        ]
    }
    
    # Verifica se existe arquivo de configuração personalizada
    if os.path.exists("build_config.ini"):
        try:
            import configparser
            parser = configparser.ConfigParser()
            parser.read("build_config.ini")
            
            if "build" in parser:
                build_section = parser["build"]
                config["app_name"] = build_section.get("app_name", config["app_name"])
                config["console_mode"] = build_section.getboolean("console_mode", config["console_mode"])
                config["debug_mode"] = build_section.getboolean("debug_mode", config["debug_mode"])
                config["icon_path"] = build_section.get("icon_path", config["icon_path"])
                config["upx_compression"] = build_section.getboolean("upx_compression", config["upx_compression"])
                
            print("✅ Configurações personalizadas carregadas!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar configurações personalizadas: {e}")
            print("   Usando configurações padrão...")
    
    return config

def generate_spec_file():
    """Gera o arquivo app.spec dinamicamente."""
    print("📝 Gerando arquivo app.spec...")
    
    # Obtém configurações
    config = get_build_config()
    system = platform.system()
    
    # Configurações baseadas no sistema operacional
    if system == "Windows":
        ffmpeg_binary = "('ffmpeg.exe', '.')"
        exe_extension = ".exe"
    else:
        ffmpeg_binary = "('ffmpeg', '.')"
        exe_extension = ""
    
    exe_name = config["app_name"] + exe_extension
    console_mode = "True" if config["console_mode"] else "False"
    debug_mode = "True" if config["debug_mode"] else "False"
    upx_enabled = "True" if config["upx_compression"] else "False"
    
    # Ícone
    icon_line = f"icon='{config['icon_path']}'," if config["icon_path"] else "icon=None,"
    
    # Exclusões
    excludes_list = str(config["exclude_modules"]).replace("'", '"')
    
    # Encontra o caminho dos assets do Whisper
    whisper_assets_path = "('whisper/assets', 'whisper/assets')"
    try:
        import whisper
        whisper_dir = os.path.dirname(whisper.__file__)
        assets_dir = os.path.join(whisper_dir, "assets")
        if os.path.exists(assets_dir):
            whisper_assets_path = f"('{assets_dir}', 'whisper/assets')"
        print(f"✅ Assets do Whisper encontrados: {assets_dir}")
    except ImportError:
        print("⚠️ Whisper não encontrado, usando caminho padrão")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Arquivo gerado automaticamente pelo build.py
# Data de geração: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import os
import platform

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[
        {ffmpeg_binary},  # FFmpeg executável
    ],
    datas=[
        {whisper_assets_path},  # Assets do Whisper
    ],
    hiddenimports=[
        'whisper',
        'whisper.model',
        'whisper.audio', 
        'whisper.decoding',
        'whisper.tokenizer',
        'ffmpeg',
        'subprocess',
        'platform',
        'pathlib',
        'glob',
        'logging',
        'gc',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'cv2',
        'moviepy',
        'transformers',
        'requests',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={excludes_list},
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{exe_name}',
    debug={debug_mode},
    bootloader_ignore_signals=False,
    strip=False,
    upx={upx_enabled},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_mode},  # Console para debug ou interface gráfica
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)
'''
    
    # Escreve o arquivo spec
    with open("app.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print(f"✅ Arquivo app.spec gerado: {exe_name}")
    print(f"   Console: {'Habilitado' if config['console_mode'] else 'Desabilitado'}")
    print(f"   Debug: {'Habilitado' if config['debug_mode'] else 'Desabilitado'}")
    print(f"   UPX: {'Habilitado' if config['upx_compression'] else 'Desabilitado'}")
    
    return True

def create_alternative_build():
    """Cria build alternativo se PyInstaller não funcionar."""
    print("🔄 Criando build alternativo...")
    
    # Comando alternativo mais simples
    system = platform.system()
    if system == "Windows":
        cmd = 'pyinstaller --onefile --windowed --name="VideoTranscriber" --add-data="whisper/assets;whisper/assets" app.py'
    else:
        cmd = 'pyinstaller --onefile --windowed --name="VideoTranscriber" --add-data="whisper/assets:whisper/assets" app.py'
    
    return run_command(cmd, "Build alternativo")

def build_executable():
    """Constrói o executável usando PyInstaller."""
    print("🏗️ Construindo executável...")
    
    # Gera o arquivo spec primeiro
    if not generate_spec_file():
        print("⚠️ Falha ao gerar spec, tentando build alternativo...")
        return create_alternative_build()
    
    # Comando de build
    build_cmd = "pyinstaller app.spec"
    
    if not run_command(build_cmd, "Build do executável"):
        print("⚠️ Build com spec falhou, tentando build alternativo...")
        return create_alternative_build()
    
    # Verifica se o executável foi criado
    system = platform.system()
    if system == "Windows":
        exe_path = "dist/VideoTranscriber.exe"
    else:
        exe_path = "dist/VideoTranscriber"
    
    if os.path.exists(exe_path):
        print(f"✅ Executável criado com sucesso: {exe_path}")
        
        # Exibe informações do arquivo
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"📏 Tamanho: {size_mb:.1f} MB")
        
        return True
    else:
        print(f"❌ Executável não encontrado em: {exe_path}")
        return False

def test_executable():
    """Testa o executável criado."""
    print("🧪 Testando executável...")
    
    system = platform.system()
    if system == "Windows":
        exe_path = "dist/VideoTranscriber.exe"
    else:
        exe_path = "dist/VideoTranscriber"
    
    if not os.path.exists(exe_path):
        print(f"❌ Executável não encontrado: {exe_path}")
        return False
    
    # Teste básico (apenas verifica se inicia)
    try:
        print("   Iniciando teste do executável...")
        # Processo em background para não travar
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda um pouco e termina
        import time
        time.sleep(2)
        process.terminate()
        
        print("✅ Executável iniciou corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar executável: {e}")
        return False

def create_installer_info():
    """Cria informações para instalação."""
    readme_build = """
# Video Transcriber - Executável

## 📦 Arquivo gerado
- **Executável**: `dist/VideoTranscriber.exe` (Windows) ou `dist/VideoTranscriber` (Linux/macOS)

## 🚀 Como usar o executável
1. Copie o arquivo executável para onde desejar
2. Execute o arquivo diretamente (duplo clique no Windows)
3. A interface gráfica será aberta automaticamente

## 📋 Requisitos do sistema
- Windows 10+ / Linux / macOS
- Pelo menos 4GB de RAM
- Conexão com internet (primeira execução para download do modelo Whisper)

## 🔧 Solução de problemas
- **Windows**: Se o antivírus bloquear, adicione à lista de exceções
- **Linux/macOS**: Dê permissão de execução: `chmod +x VideoTranscriber`

## 📁 Arquivos de saída
Os arquivos transcritos serão salvos em:
- `output/[nome-do-video]/transcription.txt`
"""
    
    with open("dist/LEIA-ME.txt", "w", encoding="utf-8") as f:
        f.write(readme_build)
    
    print("📄 Arquivo LEIA-ME.txt criado em dist/")

def main():
    """Função principal do build."""
    print("🎬 Video Transcriber - Build Automático")
    print("=" * 50)
    
    # Etapas do build
    steps = [
        ("Verificação de dependências", check_dependencies),
        ("Preparação do FFmpeg", prepare_ffmpeg),
        ("Limpeza de builds anteriores", clean_build),
        ("Construção do executável", build_executable),
        ("Teste do executável", test_executable),
        ("Criação de informações", create_installer_info),
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 Etapa: {step_name}")
        print("-" * 30)
        
        if not step_function():
            print(f"\n❌ FALHA na etapa: {step_name}")
            print("🛑 Build interrompido!")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 BUILD CONCLUÍDO COM SUCESSO!")
    print("📦 Executável disponível na pasta 'dist/'")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico durante o build: {e}")
        sys.exit(1)
