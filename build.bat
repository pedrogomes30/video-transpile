@echo off
REM Script de build para Windows - VideoTranscriber
REM Uso: build.bat [windows|linux|macos] [onefile|onedir]

setlocal EnableDelayedExpansion

REM Configurações padrão
set "TARGET_OS=windows"
set "BUILD_TYPE=onefile"

REM Processa argumentos
if not "%1"=="" set "TARGET_OS=%1"
if not "%2"=="" set "BUILD_TYPE=%2"

echo ========================================
echo VideoTranscriber Build Script
echo Target OS: %TARGET_OS%
echo Build Type: %BUILD_TYPE%
echo ========================================

REM Verifica se estamos no ambiente virtual
python -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Nao esta em um ambiente virtual Python!
    echo Execute: transpile\Scripts\activate.bat
    exit /b 1
)

REM Detecta localização do Whisper
echo [INFO] Detectando localizacao do Whisper...
for /f "tokens=*" %%i in ('python -c "import whisper, os; print(os.path.dirname(whisper.__file__))"') do set WHISPER_PATH=%%i
if "%WHISPER_PATH%"=="" (
    echo [ERROR] Nao foi possivel localizar o Whisper!
    exit /b 1
)

set "WHISPER_ASSETS=%WHISPER_PATH%\assets"
echo [INFO] Whisper assets encontrados em: %WHISPER_ASSETS%

REM Verifica se os assets existem
if not exist "%WHISPER_ASSETS%\mel_filters.npz" (
    echo [ERROR] Assets do Whisper nao encontrados!
    echo Verifique se o Whisper foi instalado corretamente.
    exit /b 1
)

REM Define nome do executável baseado no OS
set "EXE_NAME=VideoTranscriber_%TARGET_OS%"
if "%BUILD_TYPE%"=="onedir" set "EXE_NAME=%EXE_NAME%_dir"

REM Cria arquivo spec personalizado
echo [INFO] Criando arquivo spec personalizado...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo # Build script gerado automaticamente para %TARGET_OS%
echo import whisper
echo import os
echo from pathlib import Path
echo.
echo # Localiza assets do whisper
echo whisper_path = Path^(whisper.__file__^).parent
echo whisper_assets = whisper_path / 'assets'
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['app.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         # Inclui assets do whisper
echo         ^(str^(whisper_assets^), 'whisper/assets'^),
echo         # Inclui modelos se existirem
echo         ^(str^(Path.home^(^) / '.cache' / 'whisper'^), 'whisper_cache'^) if ^(Path.home^(^) / '.cache' / 'whisper'^).exists^(^) else None,
echo     ],
echo     hiddenimports=[
echo         'whisper',
echo         'torch',
echo         'torchvision',
echo         'torchaudio',
echo         'numpy',
echo         'ffmpeg',
echo         'tiktoken_ext.openai_public',
echo         'tiktoken_ext',
echo         'regex',
echo         'ftfy',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[
echo         'matplotlib',
echo         'scipy',
echo         'pandas',
echo         'jupyter',
echo         'IPython',
echo     ],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo # Remove entradas None da lista datas
echo a.datas = [x for x in a.datas if x is not None]
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
) > build_temp.spec

if "%BUILD_TYPE%"=="onefile" (
    echo [INFO] Configurando build onefile...
    (
    echo exe = EXE^(
    echo     pyz,
    echo     a.scripts,
    echo     a.binaries,
    echo     a.zipfiles,
    echo     a.datas,
    echo     [],
    echo     name='%EXE_NAME%',
    echo     debug=False,
    echo     bootloader_ignore_signals=False,
    echo     strip=False,
    echo     upx=True,
    echo     upx_exclude=[],
    echo     runtime_tmpdir=None,
    echo     console=False,
    echo     disable_windowed_traceback=False,
    echo     argv_emulation=False,
    echo     target_arch=None,
    echo     codesign_identity=None,
    echo     entitlements_file=None,
    echo ^)
    ) >> build_temp.spec
) else (
    echo [INFO] Configurando build onedir...
    (
    echo exe = EXE^(
    echo     pyz,
    echo     a.scripts,
    echo     [],
    echo     exclude_binaries=True,
    echo     name='%EXE_NAME%',
    echo     debug=False,
    echo     bootloader_ignore_signals=False,
    echo     strip=False,
    echo     upx=True,
    echo     console=False,
    echo     disable_windowed_traceback=False,
    echo     argv_emulation=False,
    echo     target_arch=None,
    echo     codesign_identity=None,
    echo     entitlements_file=None,
    echo ^)
    echo.
    echo coll = COLLECT^(
    echo     exe,
    echo     a.binaries,
    echo     a.zipfiles,
    echo     a.datas,
    echo     strip=False,
    echo     upx=True,
    echo     upx_exclude=[],
    echo     name='%EXE_NAME%',
    echo ^)
    ) >> build_temp.spec
)

REM Executa o build
echo [INFO] Iniciando build com PyInstaller...
echo [INFO] Isso pode demorar varios minutos devido ao tamanho do PyTorch e CUDA...

pyinstaller build_temp.spec

if errorlevel 1 (
    echo [ERROR] Build falhou!
    goto cleanup
)

REM Verifica se o executável foi criado
if "%BUILD_TYPE%"=="onefile" (
    if exist "dist\%EXE_NAME%.exe" (
        echo [SUCCESS] Executavel criado: dist\%EXE_NAME%.exe
        echo [INFO] Tamanho do arquivo:
        dir "dist\%EXE_NAME%.exe" | find "%EXE_NAME%.exe"
    ) else (
        echo [ERROR] Executavel nao foi criado!
        goto cleanup
    )
) else (
    if exist "dist\%EXE_NAME%\%EXE_NAME%.exe" (
        echo [SUCCESS] Aplicacao criada: dist\%EXE_NAME%\
        echo [INFO] Conteudo do diretorio:
        dir "dist\%EXE_NAME%"
    ) else (
        echo [ERROR] Aplicacao nao foi criada!
        goto cleanup
    )
)

REM Teste rápido do executável
echo [INFO] Testando se o executavel inicia...
if "%BUILD_TYPE%"=="onefile" (
    timeout 5 > nul 2>&1 & taskkill /f /im "%EXE_NAME%.exe" > nul 2>&1
    start /min "" "dist\%EXE_NAME%.exe"
    timeout 3 > nul
    taskkill /f /im "%EXE_NAME%.exe" > nul 2>&1
) else (
    timeout 5 > nul 2>&1 & taskkill /f /im "%EXE_NAME%.exe" > nul 2>&1
    start /min "" "dist\%EXE_NAME%\%EXE_NAME%.exe"
    timeout 3 > nul
    taskkill /f /im "%EXE_NAME%.exe" > nul 2>&1
)

echo [SUCCESS] Build concluido com sucesso!
echo.
echo Arquivos criados:
echo - Executavel: dist\%EXE_NAME%
echo - Spec file: %EXE_NAME%.spec
echo - Build info: build\%EXE_NAME%\
echo.
echo Para testar: cd dist && %EXE_NAME%.exe

:cleanup
REM Limpa arquivos temporários
if exist "build_temp.spec" del "build_temp.spec"

REM Renomeia spec file para nome final
if exist "build_temp.spec" move "build_temp.spec" "%EXE_NAME%.spec" > nul

echo [INFO] Limpeza concluida.
pause
