import whisper
import gc
import os
import torch
import tempfile
import ffmpeg
import requests
import urllib.request
from pathlib import Path

print(os.path.dirname(whisper.__file__))

# Variável global para callback de log
_log_callback = None

def set_log_callback(callback):
    """Define callback para logs"""
    global _log_callback
    _log_callback = callback

def log(message):
    """Log que pode ser capturado pela interface"""
    print(message)
    if _log_callback:
        _log_callback(message)

def ensure_whisper_assets():
    """Garante que os assets do Whisper existam"""
    try:
        # Primeiro tenta carregar normalmente
        import whisper.audio
        log("✓ Assets do Whisper já disponíveis")
        return True
    except Exception as e:
        log(f"⚠ Assets não encontrados, tentando corrigir: {e}")
        
        try:
            # Localiza diretório do whisper
            whisper_path = Path(whisper.__file__).parent
            assets_dir = whisper_path / "assets"
            
            # Cria diretório de assets se não existir
            assets_dir.mkdir(exist_ok=True)
            
            # URLs dos arquivos necessários (do repositório oficial do Whisper)
            mel_filters_url = "https://raw.githubusercontent.com/openai/whisper/main/whisper/assets/mel_filters.npz"
            mel_filters_path = assets_dir / "mel_filters.npz"
            
            if not mel_filters_path.exists():
                log(f"Baixando mel_filters.npz...")
                urllib.request.urlretrieve(mel_filters_url, str(mel_filters_path))
                log(f"✓ mel_filters.npz baixado para {mel_filters_path}")
            
            # Verifica se funcionou
            import whisper.audio
            log("✓ Assets do Whisper corrigidos com sucesso")
            return True
            
        except Exception as e2:
            log(f"✗ Falha ao corrigir assets: {e2}")
            return False

def is_gpu_available():
    try:
        available = torch.cuda.is_available()
        log(f"CUDA disponível: {available}")
        if available:
            log(f"Dispositivos CUDA: {torch.cuda.device_count()}")
            log(f"GPU atual: {torch.cuda.get_device_name(0)}")
        return available
    except Exception as e:
        log(f"Erro ao verificar GPU: {e}")
        return False

def get_video_duration(video_path):
    """Obtém a duração do vídeo em segundos"""
    try:
        log(f"Analisando duração do vídeo: {video_path}")
        probe = ffmpeg.probe(video_path)
        duration = float(probe['streams'][0]['duration'])
        log(f"Duração detectada: {duration:.2f} segundos")
        return duration
    except Exception as e:
        log(f"Erro ao obter duração do vídeo: {e}")
        return None

def split_audio_segments(video_path, segment_duration=30):
    """Divide o vídeo em segmentos de áudio temporários"""
    duration = get_video_duration(video_path)
    if not duration:
        log("Não foi possível obter duração, usando arquivo original")
        return [video_path]  # Se não conseguir obter duração, usa o arquivo original
    
    log(f"Dividindo vídeo em segmentos de {segment_duration}s")
    segments = []
    temp_dir = tempfile.mkdtemp()
    log(f"Diretório temporário: {temp_dir}")
    
    for start_time in range(0, int(duration), segment_duration):
        end_time = min(start_time + segment_duration, duration)
        segment_file = os.path.join(temp_dir, f"segment_{start_time}_{end_time}.wav")
        
        try:
            log(f"Criando segmento {start_time}-{end_time}s")
            (
                ffmpeg
                .input(video_path, ss=start_time, t=segment_duration)
                .output(segment_file, acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            segments.append({
                'file': segment_file,
                'start_offset': start_time,
                'end_offset': end_time
            })
            log(f"✓ Segmento criado: {segment_file}")
        except Exception as e:
            log(f"✗ Erro ao criar segmento {start_time}-{end_time}: {e}")
    
    log(f"Total de segmentos criados: {len(segments)}")
    return segments

def transcribe_audio_with_timestamps(video_path, progress_callback=None):
    log("=== INICIANDO TRANSCRIÇÃO DE ÁUDIO ===")
    
    # Garante que os assets do Whisper existam
    if not ensure_whisper_assets():
        raise Exception("Não foi possível garantir os assets do Whisper")
    
    # Detecta se há GPU disponível
    device = "cuda" if is_gpu_available() else "cpu"
    log(f"Dispositivo selecionado: {device}")
    
    # Divide o vídeo em segmentos
    log("Dividindo vídeo em segmentos...")
    segments = split_audio_segments(video_path, segment_duration=30)
    
    if len(segments) == 1 and segments[0] == video_path:
        # Se não conseguiu dividir, processa o arquivo original
        log("Processando arquivo original (sem divisão)")
        try:
            log("Carregando modelo Whisper...")
            model = whisper.load_model("small", device=device)
            log("✓ Modelo carregado com sucesso")
            
            log("Iniciando transcrição...")
            result = model.transcribe(video_path, language="Portuguese", word_timestamps=False)
            log("✓ Transcrição concluída")
            
            transcription = []
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                transcription.append({"start": start, "end": end, "text": text})
            
            log(f"Total de segmentos transcritos: {len(transcription)}")
            
            del model
            gc.collect()
            log("Modelo removido da memória")
            return transcription
            
        except Exception as e:
            log(f"✗ Erro na transcrição: {e}")
            raise
    
    # Processa segmento por segmento
    log("Processando segmentos individualmente...")
    try:
        log("Carregando modelo Whisper...")
        model = whisper.load_model("small", device=device)
        log("✓ Modelo carregado com sucesso")
    except Exception as e:
        log(f"✗ Erro ao carregar modelo: {e}")
        raise
    
    all_transcription = []
    
    for i, segment_info in enumerate(segments):
        try:
            log(f"Processando segmento {i+1}/{len(segments)}: {segment_info['start_offset']}-{segment_info['end_offset']}s")
            
            if progress_callback:
                progress = int((i / len(segments)) * 100)
                progress_callback(progress)
            
            result = model.transcribe(segment_info['file'], language="Portuguese", word_timestamps=False)
            log(f"✓ Segmento {i+1} transcrito com {len(result['segments'])} partes")
            
            # Ajusta os timestamps com o offset do segmento
            for seg in result["segments"]:
                adjusted_start = seg["start"] + segment_info['start_offset']
                adjusted_end = seg["end"] + segment_info['start_offset']
                text = seg["text"]
                all_transcription.append({
                    "start": adjusted_start, 
                    "end": adjusted_end, 
                    "text": text
                })
            
            # Remove arquivo temporário
            os.remove(segment_info['file'])
            log(f"Arquivo temporário removido: {segment_info['file']}")
            
        except Exception as e:
            log(f"✗ Erro ao transcrever segmento {i}: {e}")
    
    # Progresso final
    if progress_callback:
        progress_callback(100)
    
    log(f"Total de segmentos transcritos: {len(all_transcription)}")
    
    del model
    gc.collect()
    log("Modelo removido da memória")
    
    # Remove diretório temporário
    try:
        temp_dir = os.path.dirname(segments[0]['file'])
        os.rmdir(temp_dir)
        log(f"Diretório temporário removido: {temp_dir}")
    except Exception as e:
        log(f"Aviso: Não foi possível remover diretório temporário: {e}")

    log("=== TRANSCRIÇÃO DE ÁUDIO CONCLUÍDA ===")
    return all_transcription

def save_transcription_to_txt(transcription, output_path):
    log(f"Salvando transcrição em: {output_path}")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for segment in transcription:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                f.write(f"[{start:.2f} - {end:.2f}] {text}\n")
        log(f"✓ Arquivo salvo com {len(transcription)} segmentos")
    except Exception as e:
        log(f"✗ Erro ao salvar arquivo: {e}")
        raise
