este é um pequeno trancrissor de video em texto(legendas), usando biblioteca whisper em um ambiente local 

para buildar tem que iniciar o projeto em python e obter a pasta de assets do whisper

e usar o comando 

pyinstaller --onefile --noconsole --add-data "C:{sua localização};whisper/assets" app.py