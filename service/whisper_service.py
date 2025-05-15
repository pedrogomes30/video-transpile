import whisper
import gc
import os
print(os.path.dirname(whisper.__file__))

def transcribe_audio_with_timestamps(video_path):
    model = whisper.load_model("small")
    result = model.transcribe(video_path, language="Portuguese", word_timestamps=False)
    
    segments = result["segments"]
    transcription = []
    for segment in segments:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        transcription.append({"start": start, "end": end, "text": text})
    
    del model
    gc.collect()

    return transcription

def save_transcription_to_txt(transcription, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in transcription:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"[{start:.2f} - {end:.2f}] {text}\n")