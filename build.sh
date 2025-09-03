#!/bin/bash
# Script de build para Unix/Linux/macOS - VideoTranscriber
# Uso: ./build.sh [windows|linux|macos] [onefile|onedir]

set -e  # Sai se algum comando falhar

# Configurações padrão
TARGET_OS=${1:-linux}
BUILD_TYPE=${2:-onefile}

echo "========================================"
echo "VideoTranscriber Build Script"
echo "Target OS: $TARGET_OS"
echo "Build Type: $BUILD_TYPE"
echo "========================================"

# Verifica se estamos no ambiente virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ERROR] Não está em um ambiente virtual Python!"
    echo "Execute: source transpile/bin/activate (Linux/macOS)"
    exit 1
fi

# Detecta localização do Whisper
echo "[INFO] Detectando localização do Whisper..."
WHISPER_PATH=$(python -c "import whisper, os; print(os.path.dirname(whisper.__file__))")
if [[ -z "$WHISPER_PATH" ]]; then
    echo "[ERROR] Não foi possível localizar o Whisper!"
    exit 1
fi

WHISPER_ASSETS="$WHISPER_PATH/assets"
echo "[INFO] Whisper assets encontrados em: $WHISPER_ASSETS"

# Verifica se os assets existem
if [[ ! -f "$WHISPER_ASSETS/mel_filters.npz" ]]; then
    echo "[ERROR] Assets do Whisper não encontrados!"
    echo "Verifique se o Whisper foi instalado corretamente."
    exit 1
fi

# Define nome do executável baseado no OS
EXE_NAME="VideoTranscriber_$TARGET_OS"
if [[ "$BUILD_TYPE" == "onedir" ]]; then
    EXE_NAME="${EXE_NAME}_dir"
fi

# Define extensão baseada no OS
EXE_EXT=""
if [[ "$TARGET_OS" == "windows" ]]; then
    EXE_EXT=".exe"
fi

# Cria arquivo spec personalizado
echo "[INFO] Criando arquivo spec personalizado..."
cat > build_temp.spec << EOF
# -*- mode: python ; coding: utf-8 -*-
# Build script gerado automaticamente para $TARGET_OS
import whisper
import os
from pathlib import Path

# Localiza assets do whisper
whisper_path = Path(whisper.__file__).parent
whisper_assets = whisper_path / 'assets'

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Inclui assets do whisper
        (str(whisper_assets), 'whisper/assets'),
        # Inclui modelos se existirem (cache do usuário)
    ] + ([
        (str(Path.home() / '.cache' / 'whisper'), 'whisper_cache')
    ] if (Path.home() / '.cache' / 'whisper').exists() else []),
    hiddenimports=[
        'whisper',
        'torch',
        'torchvision',
        'torchaudio',
        'numpy',
        'ffmpeg',
        'tiktoken_ext.openai_public',
        'tiktoken_ext',
        'regex',
        'ftfy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

EOF

if [[ "$BUILD_TYPE" == "onefile" ]]; then
    echo "[INFO] Configurando build onefile..."
    cat >> build_temp.spec << EOF
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='$EXE_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF
else
    echo "[INFO] Configurando build onedir..."
    cat >> build_temp.spec << EOF
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='$EXE_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
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
    strip=False,
    upx=True,
    upx_exclude=[],
    name='$EXE_NAME',
)
EOF
fi

# Executa o build
echo "[INFO] Iniciando build com PyInstaller..."
echo "[INFO] Isso pode demorar vários minutos devido ao tamanho do PyTorch..."

pyinstaller build_temp.spec

# Verifica se o executável foi criado
if [[ "$BUILD_TYPE" == "onefile" ]]; then
    if [[ -f "dist/${EXE_NAME}${EXE_EXT}" ]]; then
        echo "[SUCCESS] Executável criado: dist/${EXE_NAME}${EXE_EXT}"
        echo "[INFO] Tamanho do arquivo:"
        ls -lh "dist/${EXE_NAME}${EXE_EXT}" | awk '{print $5, $9}'
    else
        echo "[ERROR] Executável não foi criado!"
        exit 1
    fi
else
    if [[ -f "dist/${EXE_NAME}/${EXE_NAME}${EXE_EXT}" ]]; then
        echo "[SUCCESS] Aplicação criada: dist/${EXE_NAME}/"
        echo "[INFO] Conteúdo do diretório:"
        ls -la "dist/${EXE_NAME}/"
    else
        echo "[ERROR] Aplicação não foi criada!"
        exit 1
    fi
fi

# Teste rápido do executável (só em sistemas que suportam GUI)
if [[ "$TARGET_OS" != "windows" ]] && command -v xset &> /dev/null && xset q &>/dev/null; then
    echo "[INFO] Testando se o executável inicia (GUI disponível)..."
    if [[ "$BUILD_TYPE" == "onefile" ]]; then
        timeout 3s "./dist/${EXE_NAME}${EXE_EXT}" &>/dev/null || true
    else
        timeout 3s "./dist/${EXE_NAME}/${EXE_NAME}${EXE_EXT}" &>/dev/null || true
    fi
fi

echo "[SUCCESS] Build concluído com sucesso!"
echo ""
echo "Arquivos criados:"
echo "- Executável: dist/${EXE_NAME}${EXE_EXT}"
echo "- Spec file: ${EXE_NAME}.spec"
echo "- Build info: build/${EXE_NAME}/"
echo ""
if [[ "$BUILD_TYPE" == "onefile" ]]; then
    echo "Para testar: cd dist && ./${EXE_NAME}${EXE_EXT}"
else
    echo "Para testar: cd dist/${EXE_NAME} && ./${EXE_NAME}${EXE_EXT}"
fi

# Limpa arquivos temporários e renomeia spec
if [[ -f "build_temp.spec" ]]; then
    mv "build_temp.spec" "${EXE_NAME}.spec"
fi

echo "[INFO] Limpeza concluída."
