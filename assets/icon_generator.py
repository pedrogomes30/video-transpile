"""
Gerador de ícones para a aplicação
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL não disponível. Execute: pip install Pillow")

import os

def create_app_icon():
    """Cria um ícone simples para a aplicação"""
    if not PIL_AVAILABLE:
        return None
        
    # Tamanhos de ícone comuns
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Criar imagem
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Gradiente de fundo
        for i in range(size):
            color_intensity = int(255 * (1 - i / size * 0.3))
            color = (30, 144, 255, 255)  # Azul
            draw.rectangle([(0, i), (size, i+1)], fill=color)
        
        # Desenhar símbolo de vídeo (retângulo com triângulo)
        margin = size // 8
        
        # Retângulo do vídeo
        video_rect = [margin, margin, size-margin, size-margin]
        draw.rectangle(video_rect, outline=(255, 255, 255, 255), width=max(1, size//32))
        
        # Triângulo play
        triangle_size = size // 4
        center_x, center_y = size // 2, size // 2
        triangle = [
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x - triangle_size//2, center_y + triangle_size//2),
            (center_x + triangle_size//2, center_y)
        ]
        draw.polygon(triangle, fill=(255, 255, 255, 255))
        
        # Ondas sonoras (linhas curvas)
        if size >= 48:
            wave_x = center_x + triangle_size
            for i in range(3):
                wave_radius = triangle_size//2 + i * size//16
                draw.arc(
                    [wave_x - wave_radius, center_y - wave_radius, 
                     wave_x + wave_radius, center_y + wave_radius],
                    start=-30, end=30,
                    fill=(255, 255, 255, 200),
                    width=max(1, size//64)
                )
        
        # Salvar ícone
        icon_path = f"assets/icon_{size}x{size}.png"
        img.save(icon_path, "PNG")
        print(f"Ícone criado: {icon_path}")
    
    # Criar arquivo .ico para Windows
    try:
        # Usar a imagem maior para criar .ico
        base_img = Image.open("assets/icon_256x256.png")
        ico_path = "assets/app_icon.ico"
        base_img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
        print(f"Arquivo ICO criado: {ico_path}")
        return ico_path
    except Exception as e:
        print(f"Erro ao criar ICO: {e}")
        return "assets/icon_32x32.png"

def create_simple_icon_fallback():
    """Cria um ícone básico usando apenas caracteres ASCII se PIL não estiver disponível"""
    # Criar um arquivo de texto simples que pode ser usado como referência
    icon_text = """
    Video Transcriber Icon
    ===================
    
    🎬 ▶️ 🔊
    
    Representa:
    - 🎬 Vídeo
    - ▶️ Play/Processamento  
    - 🔊 Audio/Transcrição
    """
    
    with open("assets/icon_info.txt", "w", encoding="utf-8") as f:
        f.write(icon_text)
    
    print("Arquivo de referência do ícone criado: assets/icon_info.txt")
    return None

def generate_icons():
    """Função principal para gerar ícones"""
    # Criar diretório se não existir
    os.makedirs("assets", exist_ok=True)
    
    if PIL_AVAILABLE:
        return create_app_icon()
    else:
        return create_simple_icon_fallback()

if __name__ == "__main__":
    icon_path = generate_icons()
    if icon_path:
        print(f"Ícone principal: {icon_path}")
    else:
        print("Execute 'pip install Pillow' para gerar ícones PNG/ICO")
