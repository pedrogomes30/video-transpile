# Video Transcriber (Whisper)

Este projeto é um transcritor de vídeo para texto utilizando a biblioteca [Whisper](https://github.com/openai/whisper) da OpenAI em ambiente local. Possui uma interface gráfica simples feita com Tkinter que permite selecionar vídeos, transcrever automaticamente e salvar o resultado em formato de texto com timestamps, otimizado para criação de artigos de blog com foco em SEO.

## 🎯 Objetivo

Transpilar (transcrever) vídeos em textos com formatos pré-definidos, facilitando a criação de conteúdo escrito a partir de material audiovisual.

## ✨ Funcionalidades

- 🎬 Transcrição automática de vídeos (.mp4, .mov, .avi, .mkv) para texto com timestamps
- 🖥️ Interface gráfica intuitiva usando Tkinter
- 📝 Geração de arquivo `.txt` com prompt automático para criação de artigo de blog
- 🎯 Preparação para integração com modelos de IA online
- ⏱️ Timestamps precisos para cada segmento de fala
- 🇧🇷 Transcrição otimizada para português
- 📁 Organização automática dos arquivos de saída

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Sistema operacional: Windows, macOS ou Linux
- Pelo menos 4GB de RAM disponível
- Conexão com internet para download inicial do modelo Whisper

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/pedrogomes30/video-transpile.git
cd video-transpile
```

### 2. Crie um ambiente virtual (recomendado)
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o FFmpeg (obrigatório)
```bash
# Configuração automática
python setup_ffmpeg.py

# Ou instalação manual:
# Windows: Baixe de https://ffmpeg.org e coloque ffmpeg.exe na pasta
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### 5. Verificação da instalação
```bash
# Diagnóstico completo do sistema
python test_system.py

# Verificações individuais
python -c "import whisper; print('Whisper instalado com sucesso!')"
ffmpeg -version
```

## 🎮 Como usar

### Execução do aplicativo
```bash
python app.py
```

### Passo a passo na interface:
1. **Selecionar vídeo**: Clique em "Selecionar vídeo" e escolha seu arquivo
2. **Iniciar transcrição**: Clique em "Transcrever vídeo" e aguarde o processamento
3. **Resultado**: O arquivo será salvo na pasta `output/[nome-do-video]/transcription.txt`

### Estrutura dos arquivos de saída:
```
output/
└── nome-do-video/
    └── transcription.txt    # Transcrição com timestamps e prompt para blog
```

### Formato da transcrição:
```
poderia transformar essa transcrição em um artigo para blog? com titulo e tudo mais ? focado em SEO do google?

[0.00 - 5.32] Texto do primeiro segmento
[5.32 - 12.45] Texto do segundo segmento
...
```

## 🏗️ Build do executável

### Método automático (recomendado)
```bash
python build.py
```
Este script automatizado irá:
- ✅ Verificar e instalar dependências
- ✅ Configurar o FFmpeg automaticamente
- ✅ Limpar builds anteriores
- ✅ Gerar o executável
- ✅ Testar o executável
- ✅ Criar documentação

### Método manual

#### 1. Instalação do PyInstaller
```bash
pip install pyinstaller
```

#### 2. Preparar FFmpeg
```bash
# Instalar FFmpeg automaticamente
python setup_ffmpeg.py

# Ou instalar manualmente (veja seção de Solução de Problemas)
```

#### 3. Gerar executável
```bash
pyinstaller app.spec
```

#### 4. Localização do executável
- **Windows**: `dist/VideoTranscriber.exe`
- **Linux/macOS**: `dist/VideoTranscriber`

### Configuração avançada do build

O arquivo `app.spec` é gerado automaticamente pelo `build.py` com as configurações otimizadas para seu sistema operacional.

#### Configurações personalizadas:
1. **Copie o arquivo de exemplo**:
   ```bash
   cp build_config.ini.example build_config.ini
   ```

2. **Edite as configurações** em `build_config.ini`:
   - **Nome do executável**: `app_name = MeuTranscritor`
   - **Modo console**: `console_mode = true` (para debug)
   - **Ícone personalizado**: `icon_path = assets/icon.ico`
   - **Compressão**: `upx_compression = false` (se houver problemas)

3. **Execute o build**:
   ```bash
   python build.py
   ```

#### Exemplo de configuração personalizada:
```ini
[build]
app_name = MeuVideoTranscritor
console_mode = false
debug_mode = false
icon_path = assets/meu_icon.ico
upx_compression = true
```

### Regenerar spec manualmente:
```bash
# Gerar apenas o spec sem fazer build
python -c "from build import generate_spec_file; generate_spec_file()"
```

## 📁 Estrutura do projeto

```
video-transpile/
├── app.py                          # Ponto de entrada da aplicação
├── build.py                        # Script de build automático (gera app.spec)
├── build_config.ini.example        # Exemplo de configurações de build
├── setup_ffmpeg.py                 # Configuração automática do FFmpeg
├── test_system.py                  # Diagnóstico e teste do sistema
├── config.ini                      # Arquivo de configuração da aplicação
├── requirements.txt                 # Dependências do projeto
├── readme.md                       # Documentação
├── .gitignore                      # Arquivos ignorados pelo Git
├── ffmpeg.exe                      # FFmpeg (Windows - após setup)
├── controller/                     # Controladores
│   └── transcribe_controller.py    # Lógica de controle da transcrição
├── service/                        # Serviços
│   ├── whisper_service.py          # Serviço de transcrição com Whisper
│   └── frame_capture_service.py    # Serviço de captura de frames (futuro)
├── view/                          # Interface gráfica
│   └── main_view.py               # Interface principal
├── dist/                          # Executáveis (após build)
│   ├── VideoTranscriber.exe       # Executável principal
│   └── LEIA-ME.txt                # Instruções do executável
├── build/                         # Arquivos temporários do build
├── app.spec                       # Configuração do PyInstaller (gerado)
├── build_config.ini               # Configurações personalizadas (opcional)
└── output/                        # Pasta de saída (criada automaticamente)
```

## 🔧 Dependências principais

- **openai-whisper**: Motor de transcrição de IA
- **moviepy**: Processamento de vídeo
- **opencv-python**: Manipulação de imagens e vídeo
- **ffmpeg-python**: Interface Python para FFmpeg
- **tkinter**: Interface gráfica (incluído no Python)
- **transformers**: Modelos de IA (dependência do Whisper)
- **pathlib**: Manipulação de caminhos (incluído no Python 3.4+)

## ⚠️ Solução de problemas

### Erro de FFmpeg (UnboundLocalError)
**Problema**: `local variable 'ffmpeg' referenced before assignment`

**Soluções**:
1. **Instalação automática do FFmpeg**:
   ```bash
   python setup_ffmpeg.py
   ```

2. **Instalação manual do FFmpeg**:
   
   **Windows**:
   - Baixe o FFmpeg de: https://ffmpeg.org/download.html
   - Extraia o arquivo e coloque `ffmpeg.exe` na pasta do projeto
   - Ou adicione o FFmpeg ao PATH do sistema

   **Linux**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **macOS**:
   ```bash
   brew install ffmpeg
   ```

3. **Verificação**:
   ```bash
   ffmpeg -version
   ```

### Erro de modelo não encontrado
```bash
# O Whisper baixará automaticamente o modelo na primeira execução
# Certifique-se de ter conexão com internet
```

### Erro de dependências no Linux
```bash
sudo apt-get update
sudo apt-get install python3-tk ffmpeg
```

### Erro de dependências no macOS
```bash
brew install ffmpeg
```

### Problemas de memória
- Use vídeos menores (< 1GB) para melhor performance
- Feche outros programas durante a transcrição
- O modelo "small" é usado por padrão para otimizar o uso de memória

### Problemas no executável (.exe)
- **Antivírus**: Adicione o executável à lista de exceções
- **Permissões**: Execute como administrador se necessário
- **Assets**: Certifique-se de que os assets do Whisper estão incluídos no build

## 🚀 Próximas funcionalidades

- [ ] Suporte a múltiplos idiomas
- [ ] Captura de frames em timestamps específicos
- [ ] Exportação para diferentes formatos (SRT, VTT)
- [ ] Interface web
- [ ] API REST

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

**Desenvolvido para facilitar a transcrição de vídeos e criação de conteúdo otimizado para blogs e SEO.**

