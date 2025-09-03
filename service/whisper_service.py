import whisper
import gc
import os
import subprocess
import shutil
import platform
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_ffmpeg():
    """
    Encontra o executável do FFmpeg no sistema.
    Retorna o caminho completo ou None se não encontrado.
    """
    # Primeiro, tenta encontrar no PATH do sistema
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        logger.info(f"🔍 FFmpeg encontrado no PATH: {ffmpeg_path}")
        return ffmpeg_path
    
    # Tenta encontrar em locais comuns do Windows
    if platform.system() == "Windows":
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ffmpeg.exe"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe"),
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.join(os.environ.get("TEMP", ""), "_MEI*", "ffmpeg.exe"),
            os.path.join(os.environ.get("TEMP", ""), "_MEI*", "service", "..", "ffmpeg.exe")
        ]
        
        for path in possible_paths:
            if "*" in path:
                # Para caminhos com wildcard (MEI)
                import glob
                matches = glob.glob(path)
                for match in matches:
                    if os.path.isfile(match):
                        logger.info(f"🔍 FFmpeg encontrado: {match}")
                        return match
            elif os.path.isfile(path):
                logger.info(f"🔍 FFmpeg encontrado: {path}")
                return path
    
    logger.warning("⚠️ FFmpeg não encontrado no sistema")
    return None

def validate_ffmpeg(ffmpeg_path):
    """
    Valida se o FFmpeg está funcionando corretamente.
    """
    if not ffmpeg_path or not os.path.isfile(ffmpeg_path):
        return False
        
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            logger.info("✅ FFmpeg respondendo corretamente")
            return True
        else:
            logger.error(f"❌ FFmpeg retornou erro: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao validar FFmpeg: {e}")
        return False

def ffmpeg_probe_safe(video_path):
    """
    Analisa um arquivo de vídeo usando FFmpeg de forma segura.
    """
    ffmpeg_path = None
    try:
        # Encontra o FFmpeg
        ffmpeg_path = find_ffmpeg()
        if not ffmpeg_path:
            raise Exception("FFmpeg não encontrado no sistema")
        
        logger.info(f"🔍 FFmpeg comando: {ffmpeg_path}")
        
        # Valida o FFmpeg
        if not validate_ffmpeg(ffmpeg_path):
            raise Exception("FFmpeg não está funcionando corretamente")
        
        # Executa o probe
        cmd = [
            ffmpeg_path, 
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg probe falhou: {result.stderr}")
        
        # Verifica se tem conteúdo válido
        if not result.stdout.strip():
            raise Exception("FFmpeg não retornou informações do arquivo")
            
        logger.info("✅ Arquivo de vídeo validado com sucesso")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout ao analisar arquivo com ffmpeg")
        raise Exception("Timeout ao analisar arquivo de vídeo")
    except Exception as e:
        logger.error(f"❌ Erro em ffmpeg_probe_safe: {e}")
        logger.error(f"    Tipo do erro: {type(e).__name__}")
        logger.error(f"    Video path: {video_path}")
        logger.error(f"    FFmpeg cmd: {ffmpeg_path}")
        logger.error(f"    FFMPEG_BINARY: {os.environ.get('FFMPEG_BINARY', 'não definido')}")
        raise Exception(f"Erro ao analisar arquivo: {e}")

def validate_video_file(video_path):
    """
    Valida se o arquivo de vídeo é válido e acessível.
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.isfile(video_path):
            raise Exception(f"Arquivo não encontrado: {video_path}")
        
        # Verifica se o arquivo não está vazio
        if os.path.getsize(video_path) == 0:
            raise Exception("Arquivo de vídeo está vazio")
        
        # Verifica extensão
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        file_ext = Path(video_path).suffix.lower()
        if file_ext not in valid_extensions:
            logger.warning(f"⚠️ Extensão {file_ext} pode não ser suportada")
        
        # Valida com FFmpeg
        ffmpeg_probe_safe(video_path)
        
        logger.info("✅ VALIDAÇÃO APROVADA: Arquivo de vídeo válido")
        return True
        
    except Exception as e:
        logger.error(f"✗ VALIDAÇÃO FALHOU: {e}")
        raise Exception(f"Arquivo de vídeo inválido: {e}")

def transcribe_audio_with_timestamps(video_path):
    """
    Transcreve o áudio de um vídeo usando Whisper com validação robusta.
    """
    try:
        logger.info(f"🎬 Iniciando transcrição do vídeo: {os.path.basename(video_path)}")
        
        # Valida o arquivo de vídeo antes de tentar transcrever
        validate_video_file(video_path)
        
        # Carrega o modelo Whisper
        logger.info("🤖 Carregando modelo Whisper...")
        model = whisper.load_model("small")
        
        # Executa a transcrição
        logger.info("🎙️ Executando transcrição...")
        result = model.transcribe(
            video_path, 
            language="pt",  # Português
            word_timestamps=False,
            verbose=False
        )
        
        # Processa os segmentos
        segments = result.get("segments", [])
        transcription = []
        
        for segment in segments:
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            if text:  # Só adiciona se há texto
                transcription.append({
                    "start": start, 
                    "end": end, 
                    "text": text
                })
        
        # Limpa a memória
        del model
        gc.collect()
        
        logger.info(f"✅ Transcrição concluída: {len(transcription)} segmentos processados")
        return transcription
        
    except Exception as e:
        logger.error(f"✗ ERRO NA TRANSCRIÇÃO: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        
        # Limpa a memória mesmo em caso de erro
        try:
            if 'model' in locals():
                del model
            gc.collect()
        except:
            pass
            
        raise e

def save_transcription_to_txt(transcription, output_path):
    """
    Salva a transcrição em arquivo de texto com formatação melhorada.
    """
    try:
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(transcription):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                
                # Formata o timestamp
                f.write(f"[{start:.2f} - {end:.2f}] {text}\n")
        
        logger.info(f"💾 Transcrição salva em: {output_path}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar transcrição: {e}")
        raise e