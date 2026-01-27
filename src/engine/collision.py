from game.audio_manager import play_audio

def point_in_box(px, py, box):
    """Verifica se ponto (px, py) está dentro da caixa (x, y, w, h)."""
    x, y, w, h = box
    return x <= px <= x + w and y <= py <= y + h

def simple_grab(claw, prize):
    """Detecta colisão entre garra e prêmio, capturando-o se houver contato."""
    if not claw.is_closed:
        return False

    grab_box = claw.get_grab_hitbox()
    grabbed = point_in_box(prize.x, prize.y, grab_box)
    if grabbed:
        prize.capture()
        try:
            play_audio("me-solta")
        except Exception:
            pass
    return grabbed