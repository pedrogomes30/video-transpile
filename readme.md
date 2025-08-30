# VideoTranscriber

Sistema de transcrição de vídeos usando OpenAI Whisper com interface gráfica e sistema de build automatizado.

## 🎥 Funcionalidades

- **Transcrição Inteligente**: Usa OpenAI Whisper para transcrição precisa em português
- **Suporte GPU/CPU**: Detecção automática de CUDA com fallback para CPU
- **Interface Moderna**: GUI intuitiva com logging em tempo real e barra de progresso
- **Segmentação Automática**: Processa vídeos grandes em segmentos para otimizar memória
- **Build Automatizado**: Scripts para criar executáveis multiplataforma
- **Otimização Avançada**: Diferentes perfis de build para desenvolvimento e produção

## 🚀 Início Rápido

### Usando o Executável (Recomendado)
1. Baixe o executável da seção Releases
2. Execute `VideoTranscriber.exe` (Windows) ou o equivalente para seu OS
3. Selecione um arquivo de vídeo e clique em "Transcrever"

### Executando o Código Fonte

**Pré-requisitos:**
- Python 3.8+
- FFmpeg instalado e no PATH
- GPU compatível com CUDA (opcional)

**Instalação:**
```bash
# Clone o repositório
git clone [repository-url]
cd video-transpile

# Crie um ambiente virtual
python -m venv transpile
# Windows:
transpile\Scripts\activate
# Linux/macOS:
source transpile/bin/activate

# Instale dependências
pip install -r requirements.txt

# Execute
python app.py
```

## 🔨 Build de Executáveis

### Método Simples (Recomendado)

**Windows:**
```bash
# Build de produção
build_quick.bat production

# Build de desenvolvimento
build_quick.bat development

# Build completo com modelos
build_quick.bat complete
```

**Linux/macOS:**
```bash
chmod +x build_quick.sh

# Build de produção
./build_quick.sh production

# Build de desenvolvimento  
./build_quick.sh development

# Build completo com modelos
./build_quick.sh complete
```

### Método Avançado

**Script Python Multiplataforma:**
```bash
# Build básico
python build.py

# Build otimizado para Windows
python build.py --target-os windows --optimize --test

# Build com modelos incluídos
python build.py --include-models --build-type onedir

# Build de debug
python build.py --debug --build-type onedir --test

# Limpar e rebuildar
python build.py --clean --optimize
```

**Opções do build.py:**
- `--target-os {windows,linux,macos,auto}`: Sistema alvo
- `--build-type {onefile,onedir}`: Tipo de build
- `--include-models`: Incluir modelos Whisper cached
- `--optimize`: Ativar otimizações (menor tamanho)
- `--debug`: Modo debug com console
- `--clean`: Limpar diretórios de build
- `--test`: Testar executável após build

### Perfis de Build

| Perfil | Tipo | Debug | Otimizado | Modelos | Uso |
|--------|------|-------|-----------|---------|-----|
| `development` | onedir | ✅ | ❌ | ❌ | Desenvolvimento e testes |
| `production` | onefile | ❌ | ✅ | ❌ | Distribuição padrão |
| `complete` | onefile | ❌ | ✅ | ✅ | Distribuição completa |
| `portable` | onedir | ❌ | ❌ | ✅ | Versão portátil |

## 📋 Dependências Principais

- **openai-whisper** (20231117): Engine de transcrição
- **torch** (1.13.1+cu117): PyTorch com CUDA 11.7
- **tkinter**: Interface gráfica
- **ffmpeg-python**: Processamento de vídeo
- **pyinstaller**: Criação de executáveis

## 🔧 Configuração de GPU

### NVIDIA CUDA
```bash
# Verificar compatibilidade
nvidia-smi

# Instalar PyTorch com CUDA (já incluído em requirements.txt)
pip install torch==1.13.1+cu117 -f https://download.pytorch.org/whl/torch_stable.html
```

### Teste de GPU
O aplicativo detecta automaticamente a GPU e mostra um diálogo de confirmação.

## 📁 Estrutura do Projeto

```
video-transpile/
├── app.py                 # Aplicativo principal
├── build.py              # Script de build avançado
├── build_quick.bat       # Build wrapper (Windows)
├── build_quick.sh        # Build wrapper (Unix)
├── build_config.json     # Configurações de build
├── requirements.txt      # Dependências Python
├── controller/           # Lógica de negócio
│   └── transcribe_controller.py
├── service/             # Serviços
│   ├── whisper_service.py
│   └── frame_capture_service.py
├── view/               # Interface
│   └── main_view.py
├── output/            # Saída de transcrições
├── dist/             # Executáveis gerados
└── build/           # Arquivos temporários de build
```

## � Solução de Problemas

### "mel_filters.npz not found"
```bash
# Rebuildar com assets do Whisper
python build.py --clean
```

### Erro de GPU/CUDA
```bash
# Verificar instalação CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar PyTorch
pip uninstall torch
pip install torch==1.13.1+cu117 -f https://download.pytorch.org/whl/torch_stable.html
```

### Executável muito grande
```bash
# Build otimizado
python build.py --optimize --target-os windows
```

### Erro de FFmpeg
```bash
# Windows: Baixar FFmpeg e adicionar ao PATH
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

## 📄 Logs e Debug

O aplicativo gera logs detalhados visíveis na interface. Para debug avançado:

```bash
# Build com debug habilitado
python build.py --debug --test

# Executar com logs no console
python app.py
```

## 🏗️ Desenvolvimento

### Configurar Ambiente
```bash
# Clonar e configurar
git clone [repository-url]
cd video-transpile
python -m venv transpile
source transpile/bin/activate  # ou transpile\Scripts\activate no Windows
pip install -r requirements.txt
```

### Testar Mudanças
```bash
# Build de desenvolvimento
python build.py --build-type onedir --debug --test

# Ou usar wrapper
./build_quick.sh development
```

### Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Teste com `build_quick.sh development`
4. Faça commit das mudanças
5. Abra um Pull Request

## 📝 Licença

[Adicionar informações de licença]

## 🤝 Suporte

Para problemas e sugestões, abra uma issue no repositório.
