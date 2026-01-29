from game.audio_manager import play_audio

def point_in_box(px, py, box):
    """Verifica se ponto (px, py) está dentro da caixa (x, y, w, h)."""
    x, y, w, h = box
    return x <= px <= x + w and y <= py <= y + h

def simple_grab(claw, prize):
    """Detecta colisão entre garra e prêmio, prendendo-o se houver contato."""
    # Se a garra não estiver fechada, não pega nada
    if not claw.is_closed:
        return False
        
    # Se o prêmio já estiver capturado ou sendo segurado, ignora
    if prize.captured or prize.being_held:
        return False

    grab_box = claw.get_grab_hitbox()
    grabbed = point_in_box(prize.x, prize.y, grab_box)
    
    if grabbed:
        # Prende o prêmio, mas não captura ainda
        prize.attach() 
        try:
            play_audio("me-solta")
        except Exception:
            pass
            
    return grabbed