# Video Transcriber (Whisper)

Este projeto é um transcritor de vídeo para texto (legendas), utilizando a biblioteca [Whisper](https://github.com/openai/whisper) em ambiente local. Ele possui uma interface gráfica simples feita com Tkinter, permitindo selecionar vídeos, transcrever automaticamente e salvar o resultado em arquivo de texto, pronto para ser transformado em artigo de blog otimizado para SEO.

## Funcionalidades

- Transcrição automática de vídeos (.mp4, .mov, .avi, .mkv) para texto com timestamps.
- Interface gráfica intuitiva.
- Geração de arquivo `.txt` com sugestão de prompt para criação de artigo de blog.
- Preparação para integração com modelos online.

## Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/seu-usuario/video-transcriber-whisper.git
   cd video-transcriber-whisper```

2. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```
3. Certifique-se de obter a pasta de assets do Whisper.

Uso
Execute o aplicativo:

Selecione o vídeo desejado na interface e aguarde a transcrição.

    ```sh
    python [app.py](http://_vscodecontentref_/1)
    ```
Build (Executável)
Para gerar um executável com PyInstaller:

Estrutura
app.py: inicializa a interface gráfica.
controller/: lógica de controle da transcrição.
service/: serviços de transcrição e captura de frames.
view/: interface gráfica.
Licença
MIT

Projeto criado para facilitar a transcrição de vídeos e geração de conteúdo para blogs com foco em SEO.

