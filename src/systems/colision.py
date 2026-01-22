def point_in_box(px, py, box):
    x, y, w, h = box
    return x <= px <= x + w and y <= py <= y + h

def simple_grab(claw, prize):
    if not claw.is_closed:
        return False

    grab_box = claw.get_grab_hitbox()
    grabbed = point_in_box(prize.x, prize.y, grab_box)
    if grabbed:
        prize.capture()
    return grabbed