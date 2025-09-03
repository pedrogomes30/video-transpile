import whisper
import gc
import os
<<<<<<< HEAD
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
=======
import torch
import tempfile
import ffmpeg
import shutil
import sys
from pathlib import Path
import platform
import subprocess

# Importação para som de notificação
try:
    if platform.system() == "Windows":
        import winsound
    else:
        # Para Linux/macOS, pode usar subprocess para tocar som
        import subprocess
except ImportError:
    pass  # Som não disponível

print(os.path.dirname(whisper.__file__))

# Variável global para callback de log
_log_callback = None

# Variável global para comando FFmpeg que funciona
_ffmpeg_cmd = 'ffmpeg'

def set_log_callback(callback):
    """Define callback para logs"""
    global _log_callback
    _log_callback = callback

def log(message):
    """Log que pode ser capturado pela interface"""
    print(message)
    if _log_callback:
        _log_callback(message)

def play_notification_sound(sound_type="completion"):
    """Toca um som de notificação ao finalizar a transcrição
    
    Args:
        sound_type (str): Tipo de som a tocar
            - "completion": Som de conclusão (padrão)
            - "success": Som de sucesso 
            - "alert": Som de alerta
            - "chime": Som de carrilhão
    """
    try:
        system = platform.system()
        if system == "Windows":
            # Diferentes sons do Windows baseados no tipo
            sound_map = {
                "completion": "SystemExclamation",
                "success": "SystemAsterisk", 
                "alert": "SystemHand",
                "chime": "SystemQuestion"
            }
            sound_alias = sound_map.get(sound_type, "SystemExclamation")
            winsound.PlaySound(sound_alias, winsound.SND_ALIAS)
            log(f"♪ Som de notificação tocado (Windows - {sound_type})")
            
        elif system == "Darwin":  # macOS
            # Diferentes sons do macOS
            sound_map = {
                "completion": "/System/Library/Sounds/Glass.aiff",
                "success": "/System/Library/Sounds/Hero.aiff",
                "alert": "/System/Library/Sounds/Sosumi.aiff", 
                "chime": "/System/Library/Sounds/Ping.aiff"
            }
            sound_file = sound_map.get(sound_type, "/System/Library/Sounds/Glass.aiff")
            subprocess.run(["afplay", sound_file], check=False)
            log(f"♪ Som de notificação tocado (macOS - {sound_type})")
            
        elif system == "Linux":
            # Tenta diferentes comandos de som no Linux
            try:
                subprocess.run(["paplay", "/usr/share/sounds/alsa/Front_Left.wav"], check=False, timeout=3)
                log(f"♪ Som de notificação tocado (Linux - paplay - {sound_type})")
            except:
                try:
                    subprocess.run(["aplay", "/usr/share/sounds/alsa/Front_Left.wav"], check=False, timeout=3)
                    log(f"♪ Som de notificação tocado (Linux - aplay - {sound_type})")
                except:
                    # Fallback para beep do sistema
                    subprocess.run(["echo", "-e", "\\a"], shell=True, check=False)
                    log(f"♪ Beep de notificação (Linux - fallback - {sound_type})")
        else:
            log(f"♪ Som de notificação não disponível neste sistema ({sound_type})")
    except Exception as e:
        log(f"⚠️ Não foi possível tocar som de notificação ({sound_type}): {e}")

def ensure_whisper_assets():
    """Garante que os assets do Whisper existam, especialmente em executáveis"""
    try:
        # Primeiro tenta usar os assets normalmente
        import whisper.audio
        log("✓ Assets do Whisper disponíveis")
        return True
    except Exception as e:
        log(f"⚠ Problema com assets, tentando corrigir: {e}")
        
        try:
            # Verifica se estamos rodando como executável PyInstaller
            if getattr(sys, 'frozen', False):
                log("Executável PyInstaller detectado, copiando assets...")
                
                # Diretório base do executável
                base_dir = Path(sys._MEIPASS)
                
                # Localiza diretório do whisper no sistema temporário
                whisper_temp_dir = base_dir / "whisper"
                assets_temp_dir = whisper_temp_dir / "assets"
                
                # Diretório whisper real
                whisper_real_path = Path(whisper.__file__).parent
                assets_real_dir = whisper_real_path / "assets"
                
                log(f"Diretório temp whisper: {whisper_temp_dir}")
                log(f"Diretório real whisper: {whisper_real_path}")
                
                # Cria diretório de assets se não existir
                assets_real_dir.mkdir(exist_ok=True)
                
                # Se existem assets no diretório temporário, copia para o real
                if assets_temp_dir.exists():
                    log("Copiando assets do diretório temporário...")
                    for asset_file in assets_temp_dir.glob("*"):
                        target_file = assets_real_dir / asset_file.name
                        if not target_file.exists():
                            shutil.copy2(str(asset_file), str(target_file))
                            log(f"✓ Copiado: {asset_file.name}")
                
                # Se mel_filters.npz ainda não existe, baixa da internet
                mel_filters_path = assets_real_dir / "mel_filters.npz"
                if not mel_filters_path.exists():
                    log("Baixando mel_filters.npz da internet...")
                    import urllib.request
                    url = "https://raw.githubusercontent.com/openai/whisper/main/whisper/assets/mel_filters.npz"
                    urllib.request.urlretrieve(url, str(mel_filters_path))
                    log(f"✓ Downloaded: {mel_filters_path}")
                
                # Testa novamente
                import whisper.audio
                log("✓ Assets corrigidos com sucesso")
                return True
            else:
                log("Não é executável PyInstaller, assets deveriam estar disponíveis")
                return False
                
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

def check_ffmpeg_availability():
    """Verifica se o FFmpeg está disponível e funcionando"""
    
    # Lista de possíveis localizações do FFmpeg
    ffmpeg_paths = [
        'ffmpeg',  # Sistema PATH
        './ffmpeg.exe',  # Diretório atual
        'ffmpeg/ffmpeg.exe',  # Subdiretório
        'assets/ffmpeg/ffmpeg.exe',  # Assets
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ffmpeg.exe'),  # Executável
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'ffmpeg', 'ffmpeg.exe'),
    ]
    
    # Tentar cada localização
    for ffmpeg_cmd in ffmpeg_paths:
        try:
            result = subprocess.run([ffmpeg_cmd, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                log(f"✓ FFmpeg encontrado: {ffmpeg_cmd}")
                log(f"  {version_line}")
                
                # Salvar o comando que funcionou globalmente
                global _ffmpeg_cmd
                _ffmpeg_cmd = ffmpeg_cmd
                return True, version_line
        except subprocess.TimeoutExpired:
            log(f"✗ Timeout testando: {ffmpeg_cmd}")
            continue
        except FileNotFoundError:
            continue  # Tenta próximo
        except Exception as e:
            log(f"✗ Erro testando {ffmpeg_cmd}: {e}")
            continue
    
    # Se chegou aqui, não encontrou FFmpeg
    log("✗ FFmpeg não encontrado em nenhuma localização")
    log("  Localizações testadas:")
    for path in ffmpeg_paths:
        log(f"    - {path}")
    return False, "FFmpeg não encontrado no PATH"

def ffmpeg_probe_safe(video_path):
    """Executa ffmpeg.probe usando o comando FFmpeg correto"""
    global _ffmpeg_cmd
    
    # Configurar temporariamente a variável de ambiente
    original_ffmpeg = os.environ.get('FFMPEG_BINARY')
    
    try:
        if _ffmpeg_cmd != 'ffmpeg':
            os.environ['FFMPEG_BINARY'] = os.path.abspath(_ffmpeg_cmd)
        
        return ffmpeg.probe(video_path)
    
    finally:
        # Restaurar configuração original
        if original_ffmpeg:
            os.environ['FFMPEG_BINARY'] = original_ffmpeg
        elif 'FFMPEG_BINARY' in os.environ:
            del os.environ['FFMPEG_BINARY']

def configure_ffmpeg():
    """Configura o FFmpeg para uso da biblioteca python-ffmpeg"""
    global _ffmpeg_cmd
    
    # Verificar disponibilidade primeiro
    ffmpeg_available, message = check_ffmpeg_availability()
    if ffmpeg_available:
        # Configurar variável de ambiente para python-ffmpeg
        if _ffmpeg_cmd != 'ffmpeg':
            # Se não é o comando padrão, precisa configurar o caminho
            ffmpeg_path = os.path.abspath(_ffmpeg_cmd)
            os.environ['FFMPEG_BINARY'] = ffmpeg_path
            log(f"✓ FFmpeg configurado: {ffmpeg_path}")
        return True
    else:
        log(f"✗ FFmpeg não configurado: {message}")
        return False

def validate_video_file(video_path):
    """Valida se o arquivo de vídeo existe e é acessível"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(video_path):
            log(f"✗ Arquivo não encontrado: {video_path}")
            return False, f"Arquivo não encontrado: {video_path}"
        
        # Verifica se é um arquivo (não diretório)
        if not os.path.isfile(video_path):
            log(f"✗ Caminho não é um arquivo: {video_path}")
            return False, f"Caminho não é um arquivo: {video_path}"
        
        # Verifica se o arquivo tem tamanho > 0
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            log(f"✗ Arquivo está vazio: {video_path}")
            return False, f"Arquivo está vazio: {video_path}"
        
        log(f"✓ Arquivo válido: {video_path} ({file_size:,} bytes)")
        
        # Tenta ler informações básicas do arquivo com ffmpeg
        try:
            probe = ffmpeg_probe_safe(video_path)
            
            # Verifica se tem streams de vídeo ou áudio
            video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            if not video_streams and not audio_streams:
                log(f"✗ Arquivo não contém streams de vídeo ou áudio válidos")
                return False, "Arquivo não contém streams de vídeo ou áudio válidos"
            
            # Log das informações do arquivo
            if video_streams:
                v_stream = video_streams[0]
                log(f"✓ Stream de vídeo: {v_stream.get('codec_name', 'unknown')} - {v_stream.get('width', '?')}x{v_stream.get('height', '?')}")
            
            if audio_streams:
                a_stream = audio_streams[0] 
                log(f"✓ Stream de áudio: {a_stream.get('codec_name', 'unknown')} - {a_stream.get('sample_rate', '?')} Hz")
            
            # Verifica duração
            duration = None
            for stream in probe['streams']:
                if 'duration' in stream:
                    duration = float(stream['duration'])
                    break
            
            if duration:
                log(f"✓ Duração: {duration:.2f} segundos")
            else:
                log("⚠ Duração não detectada, mas arquivo parece válido")
            
            return True, "Arquivo válido"
            
        except ffmpeg.Error as e:
            log(f"✗ Erro ao analisar arquivo com ffmpeg: {e}")
            return False, f"Erro ao analisar arquivo: {e}"
        except Exception as e:
            log(f"✗ Erro inesperado ao validar arquivo: {e}")
            return False, f"Erro inesperado: {e}"
            
    except Exception as e:
        log(f"✗ Erro ao acessar arquivo: {e}")
        return False, f"Erro ao acessar arquivo: {e}"

def get_video_duration(video_path):
    """Obtém a duração do vídeo em segundos"""
    try:
        log(f"Analisando duração do vídeo: {video_path}")
        probe = ffmpeg_probe_safe(video_path)
        duration = float(probe['streams'][0]['duration'])
        log(f"Duração detectada: {duration:.2f} segundos")
        return duration
    except Exception as e:
        log(f"Erro ao obter duração do vídeo: {e}")
        return None

def split_audio_segments(video_path, segment_duration=30):
    """Divide o vídeo em segmentos de áudio temporários"""
    # Primeiro verifica se o arquivo é válido novamente
    if not os.path.exists(video_path):
        log(f"✗ Arquivo não existe para segmentação: {video_path}")
        raise Exception(f"Arquivo não encontrado: {video_path}")
    
    duration = get_video_duration(video_path)
    if not duration:
        log("⚠ Não foi possível obter duração, tentando processar arquivo original")
        
        # Última tentativa: verifica se o arquivo pode ser lido pelo ffmpeg
        try:
            test_probe = ffmpeg_probe_safe(video_path)
            log("✓ Arquivo pode ser lido pelo ffmpeg, prosseguindo sem segmentação")
            return [video_path]  # Retorna o arquivo original se ffmpeg consegue lê-lo
        except Exception as e:
            log(f"✗ Arquivo não pode ser processado pelo ffmpeg: {e}")
            raise Exception(f"Arquivo de vídeo ilegível: {e}")
    
    # Se chegou aqui, temos duração válida
    log(f"Dividindo vídeo em segmentos de {segment_duration}s (duração total: {duration:.2f}s)")
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
                .run(quiet=True, capture_stdout=True, capture_stderr=True)
            )
            
            # Verifica se o arquivo foi criado e tem tamanho > 0
            if os.path.exists(segment_file) and os.path.getsize(segment_file) > 0:
                segments.append({
                    'file': segment_file,
                    'start_offset': start_time,
                    'end_offset': end_time
                })
                log(f"✓ Segmento criado: {segment_file} ({os.path.getsize(segment_file):,} bytes)")
            else:
                log(f"⚠ Segmento {start_time}-{end_time}s não foi criado ou está vazio")
                
        except ffmpeg.Error as e:
            log(f"✗ Erro do ffmpeg ao criar segmento {start_time}-{end_time}: {e.stderr}")
        except Exception as e:
            log(f"✗ Erro inesperado ao criar segmento {start_time}-{end_time}: {e}")
    
    if len(segments) == 0:
        log("✗ Nenhum segmento foi criado com sucesso")
        # Remove diretório temporário vazio
        try:
            os.rmdir(temp_dir)
        except:
            pass
        raise Exception("Falha ao criar segmentos de áudio do vídeo")
    
    log(f"Total de segmentos criados: {len(segments)}")
    return segments

def transcribe_audio_with_timestamps(video_path, progress_callback=None):
    log("=== INICIANDO TRANSCRIÇÃO DE ÁUDIO ===")
    
    # Configura FFmpeg primeiro
    log("Configurando FFmpeg...")
    if not configure_ffmpeg():
        log("✗ Falha na configuração do FFmpeg")
        play_notification_sound("alert")
        raise Exception("Falha na configuração do FFmpeg")
    
    # Verifica se FFmpeg está disponível
    log("Verificando FFmpeg...")
    ffmpeg_ok, ffmpeg_info = check_ffmpeg_availability()
    if not ffmpeg_ok:
        log(f"✗ FFmpeg não está disponível: {ffmpeg_info}")
        play_notification_sound("alert")
        raise Exception(f"FFmpeg não está disponível: {ffmpeg_info}")
    
    # Primeiro valida se o arquivo é válido
    log("Validando arquivo de vídeo...")
    is_valid, error_message = validate_video_file(video_path)
    
    if not is_valid:
        log(f"✗ VALIDAÇÃO FALHOU: {error_message}")
        # Toca som de erro antes de falhar
        play_notification_sound("alert")
        raise Exception(f"Arquivo de vídeo inválido: {error_message}")
    
    log("✓ Arquivo validado com sucesso")
    
    # Garante que os assets do Whisper existam
    log("Verificando assets do Whisper...")
    if not ensure_whisper_assets():
        log("✗ Assets do Whisper não disponíveis")
        play_notification_sound("alert")
        raise Exception("Não foi possível garantir os assets do Whisper")
    
    log("✓ Assets do Whisper verificados")
    
    # Detecta se há GPU disponível
    device = "cuda" if is_gpu_available() else "cpu"
    log(f"Dispositivo selecionado: {device}")
    
    # Divide o vídeo em segmentos
    log("Dividindo vídeo em segmentos...")
    segments = split_audio_segments(video_path, segment_duration=30)
    
    if len(segments) == 1 and segments[0] == video_path:
        # Se não conseguiu dividir, processa o arquivo original
        log("Processando arquivo original (sem divisão)")
        
        # Validação adicional antes de carregar o modelo
        if not os.path.exists(video_path):
            log(f"✗ Arquivo original não existe: {video_path}")
            raise Exception(f"Arquivo não encontrado: {video_path}")
        
        try:
            log("Carregando modelo Whisper...")
            model = whisper.load_model("small", device=device)
            log("✓ Modelo carregado com sucesso")
            
            log("Iniciando transcrição do arquivo original...")
            # Adiciona timeout e tratamento de erro mais robusto
            result = model.transcribe(video_path, language="Portuguese", word_timestamps=False)
            log("✓ Transcrição concluída")
            
            if not result or "segments" not in result:
                log("✗ Resultado da transcrição está vazio ou inválido")
                raise Exception("Transcrição retornou resultado inválido")
            
            transcription = []
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                transcription.append({"start": start, "end": end, "text": text})
            
            if not transcription:
                log("✗ Nenhum segmento de transcrição foi criado")
                raise Exception("Transcrição não produziu nenhum resultado")
            
            log(f"Total de segmentos transcritos: {len(transcription)}")
            
            del model
            gc.collect()
            log("Modelo removido da memória")
            
            # Toca som de conclusão
            play_notification_sound("completion")
            
            return transcription
            
        except Exception as e:
            log(f"✗ Erro na transcrição do arquivo original: {e}")
            # Limpa modelo da memória mesmo em caso de erro
            try:
                del model
                gc.collect()
            except:
                pass
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
    
    # Toca som de conclusão da transcrição
    play_notification_sound("completion")
    
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
>>>>>>> 97265ce0a4e234e2ef96a2bae8fdabdb046cbb5e
