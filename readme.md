este é um pequeno trancrissor de video em texto(legendas), usando biblioteca whisper em um ambiente local 

para buildar tem que iniciar o projeto em python e obter a pasta de assets do whisper

e usar o comando 

pyinstaller --onefile --noconsole --add-data "C:\workspace\lab\video-transpile\transpile\lib\site-packages\whisper\assets;whisper/assets" --add-binary "C:\workspace\lab\video-transpile\transpile\lib\site-packages\torch\lib\*.dll;torch/lib" app.py