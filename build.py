#!/usr/bin/env python3
"""
Script de build multiplataforma para VideoTranscriber
Automatically detects Whisper assets and creates optimized builds

Usage:
    python build.py [options]
    
Options:
    --target-os {windows,linux,macos,auto}  Target OS (default: auto-detect)
    --build-type {onefile,onedir}           Build type (default: onefile)
    --include-models                        Include cached Whisper models
    --optimize                              Enable optimizations (smaller size)
    --debug                                 Enable debug mode
    --clean                                 Clean build directories first
    --test                                  Test executable after build
    
Examples:
    python build.py --target-os windows --build-type onefile
    python build.py --optimize --include-models
    python build.py --clean --debug
"""

import argparse
import os
import sys
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
import time
from pathlib import Path
import time

def get_system_info():
    """Detect current system information"""
    system = platform.system().lower()
    if system == "darwin":
        system = "macos"
    return {
        "os": system,
        "arch": platform.machine().lower(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "is_venv": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    }

def setup_ffmpeg():
    """Configura FFmpeg para o build"""
    print("🎥 Configurando FFmpeg...")
    
    # Verificar se FFmpeg já está disponível no sistema
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg encontrado no sistema PATH")
            return True
    except:
        pass
    
    # Verificar se FFmpeg está na pasta assets
    ffmpeg_paths = [
        Path("assets/ffmpeg/ffmpeg.exe"),
        Path("assets/ffmpeg.exe"),
        Path("ffmpeg.exe")
    ]
    
    for ffmpeg_path in ffmpeg_paths:
        if ffmpeg_path.exists():
            try:
                result = subprocess.run([str(ffmpeg_path), '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ FFmpeg encontrado: {ffmpeg_path}")
                    return True
            except:
                continue
    
    # Se não encontrou, tentar configurar
    print("⚠️ FFmpeg não encontrado - tentando configurar...")
    
    try:
        # Executar o configurador
        from assets.ffmpeg_setup import setup_ffmpeg_for_build
        ffmpeg_path = setup_ffmpeg_for_build()
        if ffmpeg_path:
            print(f"✅ FFmpeg configurado: {ffmpeg_path}")
            return True
    except Exception as e:
        print(f"❌ Erro ao configurar FFmpeg: {e}")
    
    print("❌ FFmpeg não disponível - aplicação pode falhar em sistemas sem FFmpeg")
    return False

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = ['whisper', 'torch', 'PyInstaller', 'ffmpeg']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'ffmpeg':
                subprocess.run(['ffmpeg', '-version'], 
                             capture_output=True, check=True)
            elif package == 'PyInstaller':
                __import__('PyInstaller')
            else:
                __import__(package)
            print(f"✓ {package}")
        except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
            missing.append(package)
            print(f"✗ {package}")
    
    return missing

def find_whisper_assets():
    """Locate Whisper installation and assets"""
    try:
        import whisper
        whisper_path = Path(whisper.__file__).parent
        assets_path = whisper_path / "assets"
        
        required_assets = ["mel_filters.npz", "gpt2.tiktoken", "multilingual.tiktoken"]
        missing_assets = []
        
        for asset in required_assets:
            if not (assets_path / asset).exists():
                missing_assets.append(asset)
        
        return {
            "whisper_path": whisper_path,
            "assets_path": assets_path,
            "missing_assets": missing_assets,
            "valid": len(missing_assets) == 0
        }
    except ImportError:
        return {"valid": False, "error": "Whisper not installed"}

def find_whisper_models():
    """Find cached Whisper models"""
    cache_locations = [
        Path.home() / ".cache" / "whisper",
        Path.home() / "AppData" / "Local" / "whisper",  # Windows
        Path.home() / "Library" / "Caches" / "whisper"  # macOS
    ]
    
    models = []
    for cache_path in cache_locations:
        if cache_path.exists():
            models.extend(list(cache_path.glob("*.pt")))
    
    return models

def create_spec_file(args, system_info, whisper_info):
    """Create PyInstaller spec file
    
    Note: This function generates temporary .spec files that are automatically
    cleaned up after build. These files don't need to be committed to git.
    """
    
    target_os = args.target_os if args.target_os != "auto" else system_info["os"]
    exe_name = f"VideoTranscriber_{target_os}"
    
    if args.build_type == "onedir":
        exe_name += "_dir"
    
    if args.optimize:
        exe_name += "_opt"
    
    # Build data files list - fix Windows path escaping
    assets_path_str = str(whisper_info['assets_path']).replace('\\', '/')
    datas = [
        f"('{assets_path_str}', 'whisper/assets')",
    ]
    
    # Include FFmpeg if available
    ffmpeg_paths = [
        "assets/ffmpeg/ffmpeg.exe",
        "assets/ffmpeg/",
        "ffmpeg.exe"
    ]
    
    for ffmpeg_path in ffmpeg_paths:
        if os.path.exists(ffmpeg_path):
            if os.path.isfile(ffmpeg_path):
                # Corrigir escape de barras para Windows
                ffmpeg_path_fixed = ffmpeg_path.replace('\\', '/')
                datas.append(f"('{ffmpeg_path_fixed}', '.')")
                print(f"✅ FFmpeg incluído no build: {ffmpeg_path}")
            elif os.path.isdir(ffmpeg_path):
                # Incluir diretório completo
                ffmpeg_path_fixed = ffmpeg_path.replace('\\', '/')
                datas.append(f"('{ffmpeg_path_fixed}', 'ffmpeg')")
                print(f"✅ Diretório FFmpeg incluído: {ffmpeg_path}")
            break
    else:
        print("⚠️ FFmpeg não encontrado - será necessário no sistema de destino")
    
    # Include models if requested
    if args.include_models:
        models = find_whisper_models()
        if models:
            for model in models:
                datas.append(f"('{model}', 'whisper_models')")
    
    # Hidden imports - versão mais segura
    hidden_imports = [
        "'whisper'",
        "'torch'", "'torchvision'", "'torchaudio'",
        "'numpy'", "'ffmpeg'",
        "'tiktoken_ext.openai_public'", "'tiktoken_ext'",
        "'regex'",
        # Removidos temporariamente por conflitos:
        # "'ftfy'", "'more_itertools'", "'transformers'", "'tokenizers'",
    ]
    
    # Excludes for optimization
    excludes = []
    if args.optimize:
        excludes = [
            "'matplotlib'", "'scipy'", "'pandas'",
            "'jupyter'", "'IPython'", "'notebook'",
            "'qtconsole'", "'spyder'", "'anaconda'",
            "'conda'", "'setuptools'", "'pip'",
        ]
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# VideoTranscriber build spec for {target_os}
# Generated automatically by build.py

import os
from pathlib import Path

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        {','.join(datas)}
    ],
    hiddenimports=[
        {','.join(hidden_imports)}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {','.join(excludes)}
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive={str(not args.optimize).title()},
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
'''

    if args.build_type == "onefile":
        spec_content += f'''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug={str(args.debug).title()},
    bootloader_ignore_signals=False,
    strip={str(args.optimize).title()},
    upx={str(args.optimize).title()},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(args.debug).title()},
    disable_windowed_traceback={str(not args.debug).title()},
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    else:
        spec_content += f'''
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{exe_name}',
    debug={str(args.debug).title()},
    bootloader_ignore_signals=False,
    strip={str(args.optimize).title()},
    upx={str(args.optimize).title()},
    console={str(args.debug).title()},
    disable_windowed_traceback={str(not args.debug).title()},
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip={str(args.optimize).title()},
    upx={str(args.optimize).title()},
    upx_exclude=[],
    name='{exe_name}',
)
'''
    
    return spec_content, exe_name

def clean_build_dirs():
    """Clean build and dist directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def run_build(spec_file, exe_name):
    """Run PyInstaller build"""
    print(f"\\n🔨 Starting PyInstaller build...")
    print(f"   Spec file: {spec_file}")
    print(f"   Output: {exe_name}")
    print("   This may take several minutes...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", spec_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        elapsed = time.time() - start_time
        print(f"✓ Build completed in {elapsed:.1f} seconds")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed!")
        print(f"Error output:\\n{e.stderr}")
        return False

def test_executable(exe_path):
    """Test if the executable runs"""
    print(f"\\n🧪 Testing executable: {exe_path}")
    
    try:
        # Quick test - start and stop
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit then terminate
        time.sleep(3)
        process.terminate()
        
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✓ Executable starts successfully")
        return True
        
    except Exception as e:
        print(f"✗ Executable test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Build VideoTranscriber executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--target-os", 
                       choices=["windows", "linux", "macos", "auto"],
                       default="auto",
                       help="Target operating system")
    
    parser.add_argument("--build-type",
                       choices=["onefile", "onedir"],
                       default="onefile",
                       help="Build type")
    
    parser.add_argument("--include-models",
                       action="store_true",
                       help="Include cached Whisper models")
    
    parser.add_argument("--optimize",
                       action="store_true",
                       help="Enable optimizations")
    
    parser.add_argument("--debug",
                       action="store_true",
                       help="Enable debug mode")
    
    parser.add_argument("--clean",
                       action="store_true",
                       help="Clean build directories first")
    
    parser.add_argument("--test",
                       action="store_true",
                       help="Test executable after build")
    
    args = parser.parse_args()
    
    print("🚀 VideoTranscriber Build Script")
    print("=" * 40)
    
    # Get system info
    system_info = get_system_info()
    print(f"System: {system_info['os']} ({system_info['arch']})")
    print(f"Python: {system_info['python_version']}")
    print(f"Virtual Env: {'Yes' if system_info['is_venv'] else 'No'}")
    
    if not system_info['is_venv']:
        print("⚠️  Warning: Not running in virtual environment")
    
    # Check dependencies
    print("\n📦 Checking dependencies:")
    missing = check_dependencies()
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please install missing packages and try again.")
        return 1
    
    # Setup FFmpeg
    print("\n🎥 Setting up FFmpeg:")
    setup_ffmpeg()
    
    # Find Whisper assets
    print("\\n🔍 Locating Whisper assets:")
    whisper_info = find_whisper_assets()
    if not whisper_info['valid']:
        if 'error' in whisper_info:
            print(f"❌ {whisper_info['error']}")
        else:
            print(f"❌ Missing assets: {', '.join(whisper_info['missing_assets'])}")
        return 1
    
    print(f"✓ Whisper path: {whisper_info['whisper_path']}")
    print(f"✓ Assets path: {whisper_info['assets_path']}")
    
    # Find models if requested
    if args.include_models:
        models = find_whisper_models()
        print(f"✓ Found {len(models)} cached models")
    
    # Clean if requested
    if args.clean:
        print("\\n🧹 Cleaning build directories...")
        clean_build_dirs()
    
    # Create spec file
    print("\\n📝 Creating spec file...")
    spec_content, exe_name = create_spec_file(args, system_info, whisper_info)
    
    spec_file = f"{exe_name}.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print(f"✓ Created: {spec_file}")
    
    # Run build
    success = run_build(spec_file, exe_name)
    
    # Clean up spec file after build (optional)
    try:
        os.remove(spec_file)
        print(f"✓ Cleaned up: {spec_file}")
    except:
        pass  # Don't fail if can't remove
    
    if not success:
        return 1
    
    # Check output
    target_os = args.target_os if args.target_os != "auto" else system_info["os"]
    exe_ext = ".exe" if target_os == "windows" else ""
    
    if args.build_type == "onefile":
        exe_path = Path("dist") / f"{exe_name}{exe_ext}"
    else:
        exe_path = Path("dist") / exe_name / f"{exe_name}{exe_ext}"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Output: {exe_path} ({size_mb:.1f} MB)")
        
        # Test if requested
        if args.test:
            test_executable(exe_path)
            
    else:
        print(f"❌ Expected output not found: {exe_path}")
        return 1
    
    print("\\n🎉 Build completed successfully!")
    print(f"\\nTo run: {exe_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
