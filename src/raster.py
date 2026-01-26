
# =========================
# Converte retângulo (x, y, w, h) para lista de vértices de polígono.
# =========================
def rect_to_polygon(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


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
    pontos = polygon_to_int(pontos)
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
    pontos = polygon_to_int(pontos)
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

def polygon_to_int(poly):
    return [(int(round(x)), int(round(y))) for x, y in poly]

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

def draw_ellipse_points(surface, xc, yc, x, y, color):
    """Espelha ponto para os 4 quadrantes da elipse"""
    setPixel(surface, xc + x, yc + y, color)
    setPixel(surface, xc - x, yc + y, color)
    setPixel(surface, xc + x, yc - y, color)
    setPixel(surface, xc - x, yc - y, color)


def draw_ellipse(surface, center, rx, ry, color):
    """
    Desenha uma elipse usando o Algoritmo de Ponto Médio (Midpoint Ellipse Algorithm).
    
    Parâmetros:
    - surface: superfície Pygame
    - center: tupla (xc, yc) com coordenadas do centro
    - rx: raio no eixo X
    - ry: raio no eixo Y
    - color: cor da borda (R, G, B)
    
    O algoritmo divide o primeiro quadrante em duas regiões:
    - Região 1: incrementa x enquanto |slope| < 1
    - Região 2: decrementa y até y = 0
    """
    xc, yc = center
    
    # Valores iniciais (começa em (0, ry))
    x = 0
    y = ry
    
    # Quadrados dos raios (pré-calculados para evitar multiplicações repetidas)
    rx2 = rx * rx
    ry2 = ry * ry
    
    # Termos 2*a² e 2*b² (usados nos incrementos)
    two_rx2 = 2 * rx2
    two_ry2 = 2 * ry2
    
    # ===== REGIÃO 1: Incrementa x até slope = -1 =====
    # Condição: 2*b²*x < 2*a²*y
    
    # Parâmetro de decisão inicial P1 = b²(1) + a²(-b + 1/4)
    # Simplificado para inteiros: P1 = b² - a²*b + a²/4
    p1 = int(ry2 - rx2 * ry + 0.25 * rx2)
    
    # Termos incrementais para Região 1
    px = 0
    py = two_rx2 * y
    
    # Plota ponto inicial
    draw_ellipse_points(surface, xc, yc, x, y, color)
    
    # Itera enquanto a inclinação |dy/dx| < 1
    while px < py:
        x += 1
        px += two_ry2
        
        if p1 < 0:
            # Ponto médio está dentro: escolhe E (x+1, y)
            p1 += ry2 + px
        else:
            # Ponto médio está fora: escolhe SE (x+1, y-1)
            y -= 1
            py -= two_rx2
            p1 += ry2 + px - py
        
        draw_ellipse_points(surface, xc, yc, x, y, color)
    
    # ===== REGIÃO 2: Decrementa y até y = 0 =====
    # Condição: 2*b²*x >= 2*a²*y (continua de onde Região 1 parou)
    
    # Parâmetro de decisão inicial P2 para Região 2
    # P2 = b²(x + 1/2)² + a²(y - 1)² - a²b²
    p2 = int(ry2 * (x + 0.5) * (x + 0.5) + rx2 * (y - 1) * (y - 1) - rx2 * ry2)
    
    # Itera decrementando y até chegar ao eixo x
    while y > 0:
        y -= 1
        py -= two_rx2
        
        if p2 > 0:
            # Ponto médio está fora: escolhe S (x, y-1)
            p2 += rx2 - py
        else:
            # Ponto médio está dentro: escolhe SE (x+1, y-1)
            x += 1
            px += two_ry2
            p2 += rx2 - py + px
        
        draw_ellipse_points(surface, xc, yc, x, y, color)


def paint_ellipse(surface, center, rx, ry, fill_color):
    """
    Preenche uma elipse usando scanline fill.
    
    Parâmetros:
    - surface: superfície Pygame
    - center: tupla (xc, yc) com coordenadas do centro
    - rx: raio no eixo X
    - ry: raio no eixo Y
    - fill_color: cor do preenchimento (R, G, B)
    
    Algoritmo:
        Para cada scanline y de (yc - ry) até (yc + ry):
            Calcula interseções x usando equação da elipse
            Preenche pixels entre as interseções
    """
    xc, yc = center
    
    # Equação da elipse: ((x-xc)/rx)² + ((y-yc)/ry)² = 1
    # Resolvendo para x: x = xc ± rx * sqrt(1 - ((y-yc)/ry)²)
    
    for y in range(yc - ry, yc + ry + 1):
        # Calcula distância y normalizada
        dy = (y - yc) / ry if ry > 0 else 0
        
        # Verifica se está dentro dos limites da elipse
        if dy * dy > 1:
            continue
        
        # Calcula interseções x
        dx = (1 - dy * dy) ** 0.5  # sqrt(1 - dy²)
        x_offset = int(rx * dx)
        
        # Preenche scanline de (xc - x_offset) até (xc + x_offset)
        x_start = xc - x_offset
        x_end = xc + x_offset
        
        for x in range(x_start, x_end + 1):
            setPixel(surface, x, y, fill_color)