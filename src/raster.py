import pygame

def setPixel(superficie, x, y, cor):
    if 0 <= x < superficie.get_width() and 0 <= y < superficie.get_height():
        superficie.set_at((x, y), cor)

def bresenham(superficie, x0, y0, x1, y1, cor):
    # Flags para transformações
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1
    if dy < 0:
        ystep = -1
        dy = -dy

    # Bresenham clássico
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    x = x0
    y = y0

    while x <= x1:
        if steep:
            setPixel(superficie, y, x, cor)
        else:
            setPixel(superficie, x, y, cor)

        if d <= 0:
            d += incE
        else:
            d += incNE
            y += ystep

        x += 1

def drawLine(superficie, x0, y0, x1, y1, cor):
    bresenham(superficie, x0, y0, x1, y1, cor)


# =========================
# Desenho do polígono
# =========================
def drawPolygon(superficie, pontos, cor_borda):
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(superficie, x0, y0, x1, y1, cor_borda)

# =========================
# Scanline Fill
# =========================
def paintPolygon(superficie, pontos, cor_preenchimento):
    # Encontra Y mínimo e máximo
    ys = [p[1] for p in pontos]
    y_min = min(ys)
    y_max = max(ys)

    n = len(pontos)

    for y in range(y_min, y_max):
        intersecoes_x = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]

            # Ignora arestas horizontais
            if y0 == y1:
                continue

            # Garante y0 < y1
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            # Regra Ymin ≤ y < Ymax
            if y < y0 or y >= y1:
                continue

            # Calcula interseção
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes_x.append(x)

        # Ordena interseções
        intersecoes_x.sort()

        # Preenche entre pares
        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):
                x_inicio = int(round(intersecoes_x[i]))
                x_fim = int(round(intersecoes_x[i + 1]))

                for x in range(x_inicio, x_fim + 1):
                    setPixel(superficie, x, y, cor_preenchimento)

# =========================
# Flood Fill (4-conectado)
# =========================
def flood_fill_iterativo(superficie, x, y, cor_preenchimento, cor_borda):
    largura = superficie.get_width()
    altura = superficie.get_height()

    pilha = [(x, y)]

    while pilha:
        x, y = pilha.pop()

        if not (0 <= x < largura and 0 <= y < altura):
            continue

        cor_atual = superficie.get_at((x, y))[:3]

        if cor_atual == cor_borda or cor_atual == cor_preenchimento:
            continue

        setPixel(superficie, x, y, cor_preenchimento)

        pilha.append((x + 1, y))
        pilha.append((x - 1, y))
        pilha.append((x, y + 1))
        pilha.append((x, y - 1))


# Adicione ao seu raster.py

def draw_circle_points(surface, xc, yc, x, y, color):
    # Espelha o ponto para os 8 octantes
    surface.set_at((xc + x, yc + y), color)
    surface.set_at((xc - x, yc + y), color)
    surface.set_at((xc + x, yc - y), color)
    surface.set_at((xc - x, yc - y), color)
    surface.set_at((xc + y, yc + x), color)
    surface.set_at((xc - y, yc + x), color)
    surface.set_at((xc + y, yc - x), color)
    surface.set_at((xc - y, yc - x), color)

def draw_circle(surface, center, radius, color):
    """
    Desenha um círculo usando o Algoritmo do Ponto Médio (equivalente ao Bresenham).
    """
    xc, yc = center
    x = 0
    y = radius
    d = 1 - radius  # Variável de decisão inicial (para inteiros)

    draw_circle_points(surface, xc, yc, x, y, color)

    while x < y:
        if d < 0:
            # Escolhe o pixel a Leste
            d = d + 2 * x + 3
        else:
            # Escolhe o pixel a Sudeste
            d = d + 2 * (x - y) + 5
            y -= 1
        x += 1
        draw_circle_points(surface, xc, yc, x, y, color)

def draw_ellipse(surface, center, rx, ry, color):
    # Implementar Algoritmo de Ponto Médio para Elipse (Ou bresenham, circulo foi implementado com bresenham)
    pass