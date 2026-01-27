from transformations import identity, multiply_matrices, scale, translation

def viewport_window(janela, viewport):
    Wxmin, Wymin, Wxmax, Wymax = janela
    Vxmin, Vymin, Vxmax, Vymax = viewport

    sx = (Vxmax - Vxmin) / (Wxmax - Wxmin)
    sy = (Vymin - Vymax) / (Wymax - Wymin)  # <-- INVERTE O Y

    m = identity()

    # Translada janela para origem
    m = multiply_matrices(translation(-Wxmin, -Wymin), m)

    # Escala
    m = multiply_matrices(scale(sx, sy), m)

    # Ajusta o Y para o sistema do Pygame
    m = multiply_matrices(translation(Vxmin, Vymax), m)

    return m

