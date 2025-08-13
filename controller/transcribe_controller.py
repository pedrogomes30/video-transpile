from service.whisper_service import transcribe_audio_with_timestamps, save_transcription_to_txt
import os

def process_video(video_path):
    output_dir = os.path.join("output", os.path.splitext(os.path.basename(video_path))[0])
    os.makedirs(output_dir, exist_ok=True)

    transcription = transcribe_audio_with_timestamps(video_path)
    transcription_txt = os.path.join(output_dir, "transcription.txt")
    save_transcription_to_txt(transcription, transcription_txt)

    # devido a limitações do equipamento, iniciar com esta frase para utilizar em um modelo online.
    prompt = "poderia transformar essa transcrição em um artigo para blog? com titulo e tudo mais ? focado em SEO do google?\n\n"
    with open(transcription_txt, "r", encoding="utf-8") as f:
        conteudo = f.read()
    with open(transcription_txt, "w", encoding="utf-8") as f:
        f.write(prompt + conteudo)

    return transcription, transcription_txt, output_dir