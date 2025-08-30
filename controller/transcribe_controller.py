from service.whisper_service import transcribe_audio_with_timestamps, save_transcription_to_txt
import os
import traceback

def process_video(video_path):
    output_dir = os.path.join("output", os.path.splitext(os.path.basename(video_path))[0])
    os.makedirs(output_dir, exist_ok=True)

    transcription = transcribe_audio_with_timestamps(video_path)

<<<<<<< HEAD
    # Se a transcrição for uma lista de dicts, extrai o texto
    if isinstance(transcription, list):
        if all(isinstance(item, dict) and "text" in item for item in transcription):
            conteudo = "\n".join(item["text"] for item in transcription)
        else:
            conteudo = "\n".join(str(item) for item in transcription)
    else:
        conteudo = transcription
=======
    # devido a limitações do equipamento, iniciar com esta frase para utilizar em um modelo online.
    prompt = "poderia transformar essa transcrição em um artigo para blog? com titulo e tudo mais ? focado em SEO do google?\n\n"
    with open(transcription_txt, "r", encoding="utf-8") as f:
        conteudo = f.read()
    with open(transcription_txt, "w", encoding="utf-8") as f:
        f.write(prompt + conteudo)
>>>>>>> 2e4e59f22522816f35fd222356147b60de4a09b1

    # 1º arquivo: artigo para blog
    prompt_blog = "poderia transformar essa transcrição em um artigo para blog? com titulo e tudo mais ? focado em SEO do google?\n\n"
    blog_txt = os.path.join(output_dir, "arquivo para blog.txt")
    try:
        with open(blog_txt, "w", encoding="utf-8") as f:
            f.write(prompt_blog + conteudo)
    except Exception as e:
        print(f"Erro ao escrever blog_txt: {e}")
        print(traceback.format_exc())

    # 2º arquivo: apresentação Hotmart
    prompt_hotmart = (
        "Faça uma apresentação para uma aula de um curso na hotmart com base nessa transcrição da aula , ela precisa ser humanizada e com emojis, conter titulo e caso eu fale de links de material, criar uma sessão para deixar os links no fim da apresentação somente com o nome do material e o espaço para colocar o link, ah quando for escrever inventários é inventáriums, ok?\n\n"
    )
    hotmart_txt = os.path.join(output_dir, "hotmart.txt")
    try:
        with open(hotmart_txt, "w", encoding="utf-8") as f:
            f.write(prompt_hotmart + conteudo)
    except Exception as e:
        print(f"Erro ao escrever hotmart_txt: {e}")
        print(traceback.format_exc())

    # 3º arquivo: apresentação you tube
    prompt_you_tube = (
        "Crie uma descrição para um vídeo do YouTube de forma humanizada com base nessa transição. A descrição deve ser focada em seo voltado para o YouTube e no início da descrição precisa conter uma frase do tipo 'Venha aprender a fazer biscuit de forma criativa comigo, confira o inventando com Biscuit: ', pode diminuir a frase e deixar + humanizada, também deve conter emojis e o espaço para colocar os links do que foi falado na transcrição. A descrição deve ser longa para que o seo seja mais eficaz.\n\n"
    )
    you_tube_txt = os.path.join(output_dir, "youTube.txt")
    try:
        with open(you_tube_txt, "w", encoding="utf-8") as f:
            f.write(prompt_you_tube + conteudo)
    except Exception as e:
        print(f"Erro ao escrever you_tube_txt: {e}")
        print(traceback.format_exc())

    return transcription, blog_txt, hotmart_txt, you_tube_txt, output_dir