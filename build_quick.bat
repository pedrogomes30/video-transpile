@echo off
REM VideoTranscriber Build Wrapper para Windows
REM Uso: build_quick.bat [perfil] [sistema]

setlocal enabledelayedexpansion

REM Configuração padrão
set "PROFILE=production"
set "TARGET=auto"

REM Processar argumentos
if not "%1"=="" set "PROFILE=%1"
if not "%2"=="" set "TARGET=%2"

echo =========================================
echo   VideoTranscriber Build Wrapper
echo =========================================
echo.
echo Perfil: %PROFILE%
echo Sistema: %TARGET%
echo.

REM Verificar se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado no PATH
    echo Por favor instale Python ou adicione ao PATH
    pause
    exit /b 1
)

REM Verificar ambiente virtual
python -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Não está em um ambiente virtual
    echo.
    echo Quer ativar o ambiente virtual? (S/N^)
    set /p "activate_venv="
    if /i "!activate_venv!"=="S" (
        if exist "transpile\Scripts\activate.bat" (
            echo Ativando ambiente virtual...
            call transpile\Scripts\activate.bat
        ) else (
            echo ❌ Ambiente virtual não encontrado em transpile\
            pause
            exit /b 1
        )
    )
)

echo.
echo 🚀 Iniciando build...
echo.

REM Executar build baseado no perfil
if /i "%PROFILE%"=="dev" (
    python build.py --target-os %TARGET% --build-type onedir --debug --test --clean
) else if /i "%PROFILE%"=="development" (
    python build.py --target-os %TARGET% --build-type onedir --debug --test --clean
) else if /i "%PROFILE%"=="prod" (
    python build.py --target-os %TARGET% --build-type onefile --optimize --test --clean
) else if /i "%PROFILE%"=="production" (
    python build.py --target-os %TARGET% --build-type onefile --optimize --test --clean
) else if /i "%PROFILE%"=="complete" (
    python build.py --target-os %TARGET% --build-type onefile --optimize --include-models --clean
) else if /i "%PROFILE%"=="portable" (
    python build.py --target-os %TARGET% --build-type onedir --include-models --test --clean
) else (
    echo ❌ Perfil desconhecido: %PROFILE%
    echo.
    echo Perfis disponíveis:
    echo   dev/development  - Build para desenvolvimento
    echo   prod/production  - Build otimizado para distribuição
    echo   complete         - Build com modelos incluídos
    echo   portable         - Build portátil
    echo.
    pause
    exit /b 1
)

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo ❌ Build falhou!
    echo Verifique as mensagens de erro acima.
) else (
    echo.
    echo ✅ Build concluído com sucesso!
    echo.
    echo 📁 Verifique a pasta dist\ para os arquivos gerados.
    if exist "dist\" (
        echo.
        echo Arquivos criados:
        dir /b dist\
    )
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul
