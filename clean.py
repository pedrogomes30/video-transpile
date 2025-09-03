#!/usr/bin/env python3
"""
Script para limpar arquivos temporários do VideoTranscriber
"""

import os
import shutil
from pathlib import Path

def clean_temp_files():
    """Remove arquivos temporários de build"""
    files_to_clean = [
        "*.spec",           # Arquivos spec do PyInstaller
        "*.manifest",       # Manifests do PyInstaller
        "*.log",           # Logs
        "*.tmp",           # Temporários
        "*.temp"           # Temporários
    ]
    
    dirs_to_clean = [
        "build",           # Build do PyInstaller
        "dist",            # Distribuição
        "__pycache__",     # Cache Python
        "*.egg-info"       # Egg info
    ]
    
    print("🧹 Limpando arquivos temporários...")
    
    # Remove arquivos
    for pattern in files_to_clean:
        for file_path in Path(".").glob(pattern):
            try:
                file_path.unlink()
                print(f"✓ Removido: {file_path}")
            except Exception as e:
                print(f"⚠ Não foi possível remover {file_path}: {e}")
    
    # Remove diretórios
    for dir_name in dirs_to_clean:
        if dir_name.startswith("*"):
            # Pattern matching
            for dir_path in Path(".").glob(dir_name):
                if dir_path.is_dir():
                    try:
                        shutil.rmtree(dir_path)
                        print(f"✓ Removido: {dir_path}/")
                    except Exception as e:
                        print(f"⚠ Não foi possível remover {dir_path}: {e}")
        else:
            # Nome exato
            if os.path.exists(dir_name):
                try:
                    shutil.rmtree(dir_name)
                    print(f"✓ Removido: {dir_name}/")
                except Exception as e:
                    print(f"⚠ Não foi possível remover {dir_name}: {e}")
    
    print("✅ Limpeza concluída!")

if __name__ == "__main__":
    clean_temp_files()
