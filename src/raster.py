import pygame

# =========================
# Converte retângulo (x, y, w, h) para lista de vértices de polígono.
# =========================
def rect_to_polygon(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

# =========================
# Primitivas (Pixel, Linha, Polígono) - Otimizado para PixelArray
# =========================

def setPixel(surface, x, y, color):
    """Safe setPixel that handles both Surface and PixelArray"""
    try:
        # Tenta caminho rápido (PixelArray)
        if 0 <= x < surface.shape[0] and 0 <= y < surface.shape[1]:
            surface[x, y] = color
    except AttributeError:
        # Fallback para Surface padrão
        if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
            surface.set_at((x, y), color)

def bresenham(surface, x0, y0, x1, y1, color):
    # Detecta se é PixelArray para otimização
    is_pixel_array = isinstance(surface, pygame.PixelArray)
    if is_pixel_array:
        w, h = surface.shape
    else:
        w, h = surface.get_width(), surface.get_height()

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

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    x = x0
    y = y0

    while x <= x1:
        # Desenha pixels (Lógica duplicada para evitar overhead de função)
        target_x, target_y = (y, x) if steep else (x, y)
        
        if 0 <= target_x < w and 0 <= target_y < h:
            if is_pixel_array:
                surface[target_x, target_y] = color
            else:
                surface.set_at((target_x, target_y), color)

        if d <= 0:
            d += incE
        else:
            d += incNE
            y += ystep

        x += 1

def drawLine(surface, x0, y0, x1, y1, color):
    bresenham(surface, x0, y0, x1, y1, color)


# =========================
# Desenho do polígono
# =========================

def drawPolygon(surface, pontos, color):
    pontos = polygon_to_int(pontos)
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(surface, x0, y0, x1, y1, color)

# =========================
# Scanline Fill - Otimizado para PixelArray
# =========================
def paintPolygon(surface, pontos, color):
    # Detecta tipo de superfície
    is_pixel_array = isinstance(surface, pygame.PixelArray)
    if is_pixel_array:
        width, height = surface.shape
    else:
        width, height = surface.get_width(), surface.get_height()

    # Encontra Y mínimo e máximo
    pontos = polygon_to_int(pontos)
    ys = [p[1] for p in pontos]
    y_min = max(0, min(ys))
    y_max = min(height, max(ys))
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

            # Regra Ymin ≤ y < Ymax e Scanline Intersection
            if y < y0 or y >= y1:
                continue

            # Calcula interseção X
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes_x.append(x)

        # Ordena interseções
        intersecoes_x.sort()

        # Preenche entre pares
        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):
                x_start = int(round(intersecoes_x[i]))
                x_end = int(round(intersecoes_x[i + 1]))

                # Clipping Horizontal
                x_start = max(0, x_start)
                x_end = min(width - 1, x_end)

                # Desenho Rápido vs Lento
                if is_pixel_array:
                    # Otimização: Loop direto sem chamada de função
                    # + slice no lugar de for loop (roda em c = mais eficiente)
                    surface[x_start:x_end+1, y] = color
                else:
                    for x in range(x_start, x_end + 1):
                        surface.set_at((x, y), color)

# =========================
# Textured Polygon Fill
# =========================
def paintTexturedPolygon(pixel_array, screen_w, screen_h, vertices_uv, texture_matrix, tex_w, tex_h, method='standard'):
    """
    Optimized version using Direct Memory Access (PixelArray) and Texture Matrices.
    
    Args:
        pixel_array: pygame.PixelArray (locked screen surface)
        screen_w, screen_h: int (screen dimensions)
        vertices_uv: list of (x, y, u, v)
        texture_matrix: list of lists containing colors (pre-loaded texture)
        tex_w, tex_h: int (dimensions of the texture)
        method: 'standard' or 'tiling'
    """
# Extrai coordenadas Y para definir o range do scanline
    y_values = [v[1] for v in vertices_uv]
    y_min = max(0, int(min(y_values)))
    y_max = min(screen_h, int(max(y_values)))
    
    # Pré-cálculo de limites para evitar lookups repetidos
    tex_w_max = tex_w - 1
    tex_h_max = tex_h - 1
    n = len(vertices_uv)

    for y in range(y_min, y_max):
        intersecoes = []
        for i in range(n):
            x0, y0, u0, v0 = vertices_uv[i]
            x1, y1, u1, v1 = vertices_uv[(i + 1) % n]

            # Ignora arestas horizontais
            if int(y0) == int(y1): continue

            # Garante y0 < y1
            if y0 > y1:
                x0, y0, u0, v0, x1, y1, u1, v1 = x1, y1, u1, v1, x0, y0, u0, v0

            # Verifica scanline
            if y < y0 or y >= y1: continue

            # Interpolação Y (calculada uma vez por linha)
            t = (y - y0) / (y1 - y0)
            x = x0 + (x1 - x0) * t
            u = u0 + (u1 - u0) * t
            v = v0 + (v1 - v0) * t

            intersecoes.append((x, u, v))

        # Ordena interseções pelo X
        intersecoes.sort(key=lambda k: k[0])

        # Preenche os pixels entre pares de interseções
        for i in range(0, len(intersecoes), 2):
            if i + 1 >= len(intersecoes): break

            x_start_f, u_start, v_start = intersecoes[i]
            x_end_f, u_end, v_end = intersecoes[i + 1]

            x_start = int(x_start_f)
            x_end = int(x_end_f)

            span_width = x_end - x_start
            if span_width <= 0: continue

            # --- OTIMIZAÇÃO 1: Passo Incremental ---
            # Calcula quanto a textura muda por pixel (Slope)
            # Evita divisão dentro do loop
            inv_span = 1.0 / span_width
            u_step = (u_end - u_start) * inv_span
            v_step = (v_end - v_start) * inv_span

            # Clipping Horizontal e Correção de Textura
            x_draw_start = max(0, x_start)
            x_draw_end = min(screen_w, x_end)

            # Se clipamos o início (x negativo), avançamos o UV proporcionalmente
            start_skip = x_draw_start - x_start
            cur_u = u_start + (u_step * start_skip)
            cur_v = v_start + (v_step * start_skip)

            # --- OTIMIZAÇÃO 2: Separação de Loops ---
            # Evita checar "if method == tiling" para cada pixel
            
            if method == 'tiling':
                # Loop Otimizado para TILING (Cabo/Fundo)
                for x in range(x_draw_start, x_draw_end):
                    # Modulo para repetição
                    u_int = int(cur_u) % tex_w
                    v_int = int(cur_v) % tex_h

                    color = texture_matrix[u_int][v_int]
                    if color[3] >= 10: # Transparência básica
                         pixel_array[x, y] = color

                    cur_u += u_step
                    cur_v += v_step
            else:
                # Loop Otimizado para STANDARD (Objeto Único/Clamp)
                for x in range(x_draw_start, x_draw_end):
                    # Clamp manual (mais rápido que min/max repetidos)
                    u_int = int(cur_u)
                    v_int = int(cur_v)
                    
                    if u_int < 0: u_int = 0
                    elif u_int > tex_w_max: u_int = tex_w_max
                    
                    if v_int < 0: v_int = 0
                    elif v_int > tex_h_max: v_int = tex_h_max

                    color = texture_matrix[u_int][v_int]
                    if color[3] >= 10:
                        pixel_array[x, y] = color

                    cur_u += u_step
                    cur_v += v_step

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

def paintTexturedEllipse(pixel_array, screen_w, screen_h, center, rx, ry, texture_matrix, tex_w, tex_h):
    """
    Preenche uma elipse com uma textura usando PixelArray e Matrizes (Otimizado).
    
    Parâmetros:
    - pixel_array: pygame.PixelArray (Acesso direto à memória da tela)
    - screen_w, screen_h: Dimensões da tela (para clipping)
    - center: tupla (xc, yc) com coordenadas do centro
    - rx: raio no eixo X
    - ry: raio no eixo Y
    - texture_matrix: Matriz 2D de cores [x][y] (textura pré-carregada)
    - tex_w, tex_h: Dimensões da textura
    """
    xc, yc = center
    
    # Altura e largura totais da elipse
    total_width = 2 * rx
    total_height = 2 * ry
    
    # Evita divisão por zero
    if total_width == 0 or total_height == 0:
        return

    # Otimização: define limites de Y na tela (Clipping Vertical)
    y_start = max(0, yc - ry)
    y_end = min(screen_h - 1, yc + ry)

    # Loop Y (Scanline)
    for y in range(y_start, y_end + 1):
        # Verifica se está dentro da elipse geometricamente
        dy = (y - yc) / ry if ry > 0 else 0
        term = 1 - dy * dy
        
        if term < 0: 
            continue
        
        dx = term ** 0.5
        x_offset = int(rx * dx)
        
        # Define o span horizontal (início e fim do preenchimento desta linha)
        x_start = xc - x_offset
        x_end = xc + x_offset
        
        # Clipping Horizontal (impede desenhar fora da tela e crashar o array)
        x_draw_start = max(0, x_start)
        x_draw_end = min(screen_w - 1, x_end)
        
        # Se o span estiver totalmente fora da tela, pula
        if x_draw_start > x_draw_end:
            continue

        # --- Calculo do v (vertical textura) ---
        # Normaliza Y (0.0 a 1.0)
        norm_y = (y - (yc - ry)) / total_height
        v = int(norm_y * tex_h)
        v = max(0, min(v, tex_h - 1))

        # Otimização: Pré-cálculo para evitar divisão no loop interno
        inv_total_width = 1.0 / total_width
        
        u_step = inv_total_width * tex_w
        current_u = ((x_draw_start - (xc - rx)) * inv_total_width) * tex_w
        # Loop X
        for x in range(x_draw_start, x_draw_end + 1):
            u = int(current_u)
            u = max(0, min(u, tex_w - 1))
            current_u += u_step

            # FAST LOOKUP: Acesso direto à lista de listas (sem overhead de função)
            color = texture_matrix[u][v]
            
            # Checagem de transparência (Assume tupla RGBA ou RGB)
            # Se for RGBA e Alpha < 10, pula
            if color[3] >= 10:
                # FAST WRITE: Escrita direta na memória da tela
                pixel_array[x, y] = color