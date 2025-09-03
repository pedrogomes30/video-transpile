from service.whisper_service import transcribe_audio_with_timestamps, save_transcription_to_txt, set_log_callback, log, play_notification_sound
import os
import traceback

def process_video(video_path, progress_callback=None, log_callback=None):
    # Configura callback de log
    if log_callback:
        set_log_callback(log_callback)
    
    log("=== INICIANDO PROCESSAMENTO DO VÍDEO ===")
    log(f"Arquivo: {video_path}")
    
    # Cria diretório de saída
    output_dir = os.path.join("output", os.path.splitext(os.path.basename(video_path))[0])
    log(f"Diretório de saída: {output_dir}")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        log("✓ Diretório de saída criado")
    except Exception as e:
        log(f"✗ Erro ao criar diretório: {e}")
        raise

    # Transcreve o áudio
    log("Iniciando transcrição de áudio...")
    transcription = transcribe_audio_with_timestamps(video_path, progress_callback)

    if not transcription:
        log("✗ Transcrição retornou vazia!")
        raise Exception("Transcrição falhou - resultado vazio")
    
    log(f"✓ Transcrição concluída com {len(transcription)} segmentos")

    # Processa conteúdo da transcrição
    if isinstance(transcription, list):
        if all(isinstance(item, dict) and "text" in item for item in transcription):
            conteudo = "\n".join(item["text"] for item in transcription)
            log("✓ Conteúdo extraído dos segmentos")
        else:
            conteudo = "\n".join(str(item) for item in transcription)
            log("⚠ Conteúdo extraído como string")
    else:
        conteudo = transcription
        log("⚠ Transcrição não é uma lista")

    log(f"Tamanho do conteúdo: {len(conteudo)} caracteres")
    
    if len(conteudo.strip()) == 0:
        log("✗ Conteúdo da transcrição está vazio!")
        raise Exception("Conteúdo da transcrição está vazio")

    # 1º arquivo: artigo para blog
    log("Criando arquivo para blog...")
    prompt_blog = "poderia transformar essa transcrição em um artigo para blog? com titulo e tudo mais ? focado em SEO do google?\n\n"
    blog_txt = os.path.join(output_dir, "arquivo para blog.txt")
    try:
        with open(blog_txt, "w", encoding="utf-8") as f:
            f.write(prompt_blog + conteudo)
        log(f"✓ Arquivo blog criado: {blog_txt}")
    except Exception as e:
        log(f"✗ Erro ao escrever blog_txt: {e}")
        print(traceback.format_exc())
        raise

    # 2º arquivo: apresentação Hotmart
    log("Criando arquivo para Hotmart...")
    prompt_hotmart = (
        "Faça uma apresentação para uma aula de um curso na hotmart com base nessa transcrição da aula , ela precisa ser humanizada e com emojis, conter titulo e caso eu fale de links de material, criar uma sessão para deixar os links no fim da apresentação somente com o nome do material e o espaço para colocar o link, ah quando for escrever inventários é inventáriums, ok?\n\n"
    )
    hotmart_txt = os.path.join(output_dir, "hotmart.txt")
    try:
        with open(hotmart_txt, "w", encoding="utf-8") as f:
            f.write(prompt_hotmart + conteudo)
        log(f"✓ Arquivo Hotmart criado: {hotmart_txt}")
    except Exception as e:
        log(f"✗ Erro ao escrever hotmart_txt: {e}")
        print(traceback.format_exc())
        raise

    # 3º arquivo: apresentação you tube
    log("Criando arquivo para YouTube...")
    prompt_you_tube = (
        "Crie uma descrição para um vídeo do YouTube de forma humanizada com base nessa transição. A descrição deve ser focada em seo voltado para o YouTube e no início da descrição precisa conter uma frase do tipo 'Venha aprender a fazer biscuit de forma criativa comigo, confira o inventando com Biscuit: ', pode diminuir a frase e deixar + humanizada, também deve conter emojis e o espaço para colocar os links do que foi falado na transcrição. A descrição deve ser longa para que o seo seja mais eficaz.\n\n"
    )
    you_tube_txt = os.path.join(output_dir, "youTube.txt")
    try:
        with open(you_tube_txt, "w", encoding="utf-8") as f:
            f.write(prompt_you_tube + conteudo)
        log(f"✓ Arquivo YouTube criado: {you_tube_txt}")
    except Exception as e:
        log(f"✗ Erro ao escrever you_tube_txt: {e}")
        print(traceback.format_exc())
        raise

    log("=== PROCESSAMENTO CONCLUÍDO COM SUCESSO ===")
    
    # Toca som final de sucesso (diferente do som de conclusão da transcrição)
    play_notification_sound("success")
    
    return transcription, blog_txt, hotmart_txt, you_tube_txt, output_dir