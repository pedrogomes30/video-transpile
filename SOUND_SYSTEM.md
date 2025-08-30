# Sistema de Notificação Sonora - VideoTranscriber

## Funcionalidade
O VideoTranscriber agora possui um sistema completo de notificação sonora que toca diferentes sons em momentos específicos do processo de transcrição.

## Tipos de Sons

### 1. Som de Conclusão (`completion`)
- **Quando toca**: Ao finalizar a transcrição de áudio
- **Som Windows**: SystemExclamation
- **Som macOS**: Glass.aiff
- **Objetivo**: Notificar que a etapa de transcrição foi concluída

### 2. Som de Sucesso (`success`) 
- **Quando toca**: Ao finalizar todo o processamento (criação de arquivos)
- **Som Windows**: SystemAsterisk
- **Som macOS**: Hero.aiff
- **Objetivo**: Notificar que todo o processo foi concluído com sucesso

### 3. Som de Alerta (`alert`)
- **Quando toca**: Quando ocorre um erro durante o processo
- **Som Windows**: SystemHand
- **Som macOS**: Sosumi.aiff
- **Objetivo**: Notificar que houve um problema

### 4. Som de Carrilhão (`chime`)
- **Quando toca**: Reservado para uso futuro
- **Som Windows**: SystemQuestion
- **Som macOS**: Ping.aiff
- **Objetivo**: Notificações especiais

## Compatibilidade

### Windows
- Usa `winsound.PlaySound()` com sons do sistema
- Sons: SystemExclamation, SystemAsterisk, SystemHand, SystemQuestion

### macOS
- Usa `afplay` com arquivos de som do sistema
- Sons: Glass.aiff, Hero.aiff, Sosumi.aiff, Ping.aiff

### Linux
- Tenta `paplay` ou `aplay` com arquivos de som padrão
- Fallback para beep do sistema (`echo -e "\\a"`)

## Implementação

### Arquivos Modificados:
1. **`service/whisper_service.py`**:
   - Função `play_notification_sound(sound_type)`
   - Som de conclusão da transcrição

2. **`controller/transcribe_controller.py`**:
   - Som de sucesso ao finalizar processamento

3. **`view/main_view.py`**:
   - Som de alerta em caso de erro

### Uso:
```python
from service.whisper_service import play_notification_sound

# Som de conclusão
play_notification_sound("completion")

# Som de sucesso  
play_notification_sound("success")

# Som de alerta
play_notification_sound("alert")

# Som de carrilhão
play_notification_sound("chime")
```

## Teste
Execute `python test_sound.py` para testar todos os tipos de som disponíveis.

## Benefícios
- **Feedback Imediato**: O usuário sabe quando cada etapa é concluída
- **Trabalho em Background**: Permite trabalhar em outras tarefas enquanto aguarda
- **Detecção de Erros**: Som diferenciado para problemas
- **Multiplataforma**: Funciona em Windows, macOS e Linux
- **Não Intrusivo**: Usa sons do sistema, respeitando configurações do usuário

## Notas Técnicas
- Os sons são tocados de forma assíncrona para não bloquear a interface
- Em caso de falha ao tocar som, o processo continua normalmente
- Cada sistema operacional usa seus próprios sons nativos
- Fallbacks garantem funcionamento mesmo em sistemas limitados
