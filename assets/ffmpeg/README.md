# assets/ffmpeg/
# Este diretório é criado automaticamente durante o build
# O FFmpeg é baixado dinamicamente e não precisa ser commitado no Git

## Como funciona:

1. **Durante o build**: `assets/ffmpeg_setup.py` baixa FFmpeg automaticamente
2. **No .gitignore**: assets/ffmpeg/ está excluído do Git
3. **No executável**: FFmpeg é incluído normalmente

## Para rebuilds:

Se precisar fazer novo build em outro ambiente:
```bash
python assets/ffmpeg_setup.py  # Baixa FFmpeg
python build.py                # Faz o build
```

O FFmpeg será baixado automaticamente se não existir.
