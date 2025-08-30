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

### 4. Verificação da instalação
```bash
python -c "import whisper; print('Whisper instalado com sucesso!')"
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

### Instalação do PyInstaller
```bash
pip install pyinstaller
```

### Gerar executável
```bash
pyinstaller app.spec
```

O executável será criado na pasta `dist/` e incluirá automaticamente os assets necessários do Whisper.

### Para gerar um novo spec file (se necessário):
```bash
pyinstaller --onefile --windowed --add-data "caminho/para/whisper/assets:whisper/assets" app.py
```

## 📁 Estrutura do projeto

```
video-transpile/
├── app.py                          # Ponto de entrada da aplicação
├── app.spec                        # Configuração do PyInstaller
├── requirements.txt                 # Dependências do projeto
├── readme.md                       # Documentação
├── controller/                     # Controladores
│   └── transcribe_controller.py    # Lógica de controle da transcrição
├── service/                        # Serviços
│   ├── whisper_service.py          # Serviço de transcrição com Whisper
│   └── frame_capture_service.py    # Serviço de captura de frames (futuro)
├── view/                          # Interface gráfica
│   └── main_view.py               # Interface principal
└── output/                        # Pasta de saída (criada automaticamente)
```

## 🔧 Dependências principais

- **openai-whisper**: Motor de transcrição de IA
- **moviepy**: Processamento de vídeo
- **opencv-python**: Manipulação de imagens e vídeo
- **tkinter**: Interface gráfica (incluído no Python)
- **transformers**: Modelos de IA (dependência do Whisper)

## ⚠️ Solução de problemas

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

