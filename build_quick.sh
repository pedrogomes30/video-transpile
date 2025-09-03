#!/bin/bash
# VideoTranscriber Build Wrapper para Unix/Linux/macOS
# Uso: ./build_quick.sh [perfil] [sistema]

set -e  # Sair em caso de erro

# Configuração padrão
PROFILE="${1:-production}"
TARGET="${2:-auto}"

echo "========================================="
echo "   VideoTranscriber Build Wrapper"
echo "========================================="
echo
echo "Perfil: $PROFILE"
echo "Sistema: $TARGET"
echo

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado no PATH"
    echo "Por favor instale Python"
    exit 1
fi

# Usar python3 se disponível, senão python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Usando: $($PYTHON_CMD --version)"

# Verificar ambiente virtual
if ! $PYTHON_CMD -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>/dev/null; then
    echo "⚠️  Não está em um ambiente virtual"
    echo
    echo -n "Quer ativar o ambiente virtual? (s/N): "
    read -r activate_venv
    if [[ "$activate_venv" =~ ^[Ss]$ ]]; then
        if [ -f "transpile/bin/activate" ]; then
            echo "Ativando ambiente virtual..."
            source transpile/bin/activate
        else
            echo "❌ Ambiente virtual não encontrado em transpile/"
            exit 1
        fi
    fi
fi

echo
echo "🚀 Iniciando build..."
echo

# Executar build baseado no perfil
case "$PROFILE" in
    "dev"|"development")
        $PYTHON_CMD build.py --target-os "$TARGET" --build-type onedir --debug --test --clean
        ;;
    "prod"|"production")
        $PYTHON_CMD build.py --target-os "$TARGET" --build-type onefile --optimize --test --clean
        ;;
    "complete")
        $PYTHON_CMD build.py --target-os "$TARGET" --build-type onefile --optimize --include-models --clean
        ;;
    "portable")
        $PYTHON_CMD build.py --target-os "$TARGET" --build-type onedir --include-models --test --clean
        ;;
    *)
        echo "❌ Perfil desconhecido: $PROFILE"
        echo
        echo "Perfis disponíveis:"
        echo "  dev/development  - Build para desenvolvimento"
        echo "  prod/production  - Build otimizado para distribuição"
        echo "  complete         - Build com modelos incluídos"
        echo "  portable         - Build portátil"
        echo
        exit 1
        ;;
esac

# Verificar resultado
if [ $? -eq 0 ]; then
    echo
    echo "✅ Build concluído com sucesso!"
    echo
    echo "📁 Verifique a pasta dist/ para os arquivos gerados."
    if [ -d "dist" ]; then
        echo
        echo "Arquivos criados:"
        ls -la dist/
    fi
else
    echo
    echo "❌ Build falhou!"
    echo "Verifique as mensagens de erro acima."
    exit 1
fi

echo
echo "Pressione Enter para continuar..."
read -r
