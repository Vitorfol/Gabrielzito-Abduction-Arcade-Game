import pygame


def rect_to_polygon(rect):
    """
    Converte retângulo (x, y, w, h) para lista de vértices de polígono.
    """
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def setPixel(surface, x, y, color):
    """Safe setPixel that handles both Surface and PixelArray"""
    try:
        # Tenta PixelArray
        if 0 <= x < surface.shape[0] and 0 <= y < surface.shape[1]:
            surface[x, y] = color
    except AttributeError:
        # Fallback para Surface padrão
        if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
            surface.set_at((x, y), color)


def bresenham(surface, x0, y0, x1, y1, color):
    """Desenha linha usando algoritmo de Bresenham. Detecta se é PixelArray para otimização."""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
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
        # Desenha pixels
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
    """Desenha linha entre dois pontos."""
    bresenham(surface, x0, y0, x1, y1, color)


def drawPolygon(surface, pontos, color):
    """Desenha contorno de polígono."""
    pontos = polygon_to_int(pontos)
    n = len(pontos)
    for i in range(n):
        x0, y0 = pontos[i]
        x1, y1 = pontos[(i + 1) % n]
        bresenham(surface, x0, y0, x1, y1, color)


def paintPolygon(pixel_array, pontos, color):
    """Preenche polígono usando algoritmo scanline."""
    w, h = pixel_array.shape

    # Converte para int se necessário
    if isinstance(color, tuple):
        color = pixel_array.surface.map_rgb(color)

    # Encontra Y mínimo e máximo
    ys = [int(p[1]) for p in pontos]
    y_min = max(0, min(ys))
    y_max = min(h, max(ys))

    n = len(pontos)
    pontos_int = [(int(p[0]), int(p[1])) for p in pontos]

    for y in range(y_min, y_max):
        intersecoes_x = []
        for i in range(n):
            x0, y0 = pontos_int[i]
            x1, y1 = pontos_int[(i + 1) % n]

            if y0 == y1:
                continue  # Ignora arestas horizontais
            if y0 > y1:  # Garante y0 < y1
                x0, y0, x1, y1 = x1, y1, x0, y0
            if y < y0 or y >= y1:
                continue  # Verifica scanline

            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)  # Calcula interseção X
            intersecoes_x.append(x)

        intersecoes_x.sort()  # Ordena interseções

        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):  # Clipping Horizontal (par de interseções)
                x_start = max(0, int(intersecoes_x[i]))
                x_end = min(w - 1, int(intersecoes_x[i + 1]))

                # Otimização: Loop direto sem chamada de função
                # + slice no lugar de for loop (roda em c = mais eficiente)
                if x_start <= x_end:
                    pixel_array[x_start : x_end + 1, y] = color


def paintTexturedPolygon(
    pixel_array,
    screen_w,
    screen_h,
    vertices_uv,
    texture_matrix,
    tex_w,
    tex_h,
    method="standard",
):
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
            if int(y0) == int(y1):
                continue

            # Garante y0 < y1
            if y0 > y1:
                x0, y0, u0, v0, x1, y1, u1, v1 = x1, y1, u1, v1, x0, y0, u0, v0

            # Verifica scanline
            if y < y0 or y >= y1:
                continue

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
            if i + 1 >= len(intersecoes):
                break

            x_start_f, u_start, v_start = intersecoes[i]
            x_end_f, u_end, v_end = intersecoes[i + 1]

            x_start = int(x_start_f)
            x_end = int(x_end_f)

            span_width = x_end - x_start
            if span_width <= 0:
                continue

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

            if method == "tiling":
                # Loop Otimizado para TILING (Cabo/Fundo)
                for x in range(x_draw_start, x_draw_end):
                    # Modulo para repetição
                    u_int = int(cur_u) % tex_w
                    v_int = int(cur_v) % tex_h

                    color = texture_matrix[u_int][v_int]
                    if color[3] >= 10:  # Transparência básica
                        pixel_array[x, y] = color

                    cur_u += u_step
                    cur_v += v_step
            else:
                # Loop Otimizado para STANDARD (Objeto Único/Clamp)
                for x in range(x_draw_start, x_draw_end):
                    # Clamp manual (mais rápido que min/max repetidos)
                    u_int = int(cur_u)
                    v_int = int(cur_v)

                    if u_int < 0:
                        u_int = 0
                    elif u_int > tex_w_max:
                        u_int = tex_w_max

                    if v_int < 0:
                        v_int = 0
                    elif v_int > tex_h_max:
                        v_int = tex_h_max

                    color = texture_matrix[u_int][v_int]
                    if color[3] >= 10:
                        pixel_array[x, y] = color

                    cur_u += u_step
                    cur_v += v_step


def polygon_to_int(poly):
    """Converte polígono de floats para inteiros arredondados."""
    return [(int(round(x)), int(round(y))) for x, y in poly]


def draw_circle_points(pixel_array, xc, yc, x, y, color):
    """
    Espelha ponto nos 8 octantes do círculo diretamente no PixelArray.
    """
    w, h = pixel_array.shape
    points = [
        (xc + x, yc + y),
        (xc - x, yc + y),
        (xc + x, yc - y),
        (xc - x, yc - y),
        (xc + y, yc + x),
        (xc - y, yc + x),
        (xc + y, yc - x),
        (xc - y, yc - x),
    ]

    for px, py in points:
        if 0 <= px < w and 0 <= py < h:
            pixel_array[px, py] = color


def draw_circle(pixel_array, center, radius, color):
    """
    Desenha um círculo usando o Algoritmo do Ponto Médio.
    Recebe PixelArray.
    """
    xc, yc = center
    x = 0
    y = radius
    d = 1 - radius

    # Desenha os pontos iniciais
    draw_circle_points(pixel_array, xc, yc, x, y, color)

    while x < y:
        if d < 0:
            d = d + 2 * x + 3
        else:
            d = d + 2 * (x - y) + 5
            y -= 1
        x += 1
        draw_circle_points(pixel_array, xc, yc, x, y, color)


def flood_fill_iterativo(pixel_array, x, y, fill_color, border_color):
    """
    Preenche área usando flood fill 4-conectado.
    ERecebe PixelArray.
    Converte cores automaticamente se forem passadas como tuplas.
    """
    w, h = pixel_array.shape

    # Converte tuplas (R,G,B) para inteiros mapeados, se necessário
    if isinstance(fill_color, tuple):
        fill_color = pixel_array.surface.map_rgb(fill_color)
    if isinstance(border_color, tuple):
        border_color = pixel_array.surface.map_rgb(border_color)

    # Verifica limites iniciais
    if not (0 <= x < w and 0 <= y < h):
        return

    # Obtém a cor atual (inteiro)
    current_color = pixel_array[x, y]

    # Se já for a cor de borda ou de preenchimento, para
    if current_color == border_color or current_color == fill_color:
        return

    stack = [(x, y)]

    while stack:
        cx, cy = stack.pop()

        if not (0 <= cx < w and 0 <= cy < h):
            continue

        val = pixel_array[cx, cy]

        if val == border_color or val == fill_color:
            continue

        pixel_array[cx, cy] = fill_color

        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))

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


def paintTexturedEllipse(
    pixel_array, screen_w, screen_h, center, rx, ry, texture_matrix, tex_w, tex_h
):
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

        dx = term**0.5
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

            # Se Alpha < 10, pula
            if color[3] >= 10:
                pixel_array[x, y] = color


def draw_text_raster(pixel_array, font, text, x, y, color):
    """
    Renderiza texto desenhando pixel por pixel.

    Args:
        pixel_array: O PixelArray da tela principal (bloqueado).
        font: A fonte pygame carregada.
        text: A string a ser escrita.
        x, y: Posição superior esquerda.
        color: A cor do texto.
    """
    # Renderiza o texto numa superfície temporária (na memória, não na tela)
    text_surface = font.render(text, True, color)
    w, h = text_surface.get_width(), text_surface.get_height()

    # Obtém dimensões da tela para evitar erro de índice
    screen_w, screen_h = pixel_array.shape

    # Itera sobre os pixels da superfície do texto
    for px in range(w):
        for py in range(h):
            # Pega a cor do pixel do texto
            curr_color = text_surface.get_at((px, py))

            # Só desenha se não for transparente
            if curr_color.a > 10:
                draw_x = x + px
                draw_y = y + py

                # Verifica limites da tela (Clipping)
                if 0 <= draw_x < screen_w and 0 <= draw_y < screen_h:
                    pixel_array[draw_x, draw_y] = curr_color


def draw_gradient_rect(pixel_array, x, y, w, h, cor_topo, cor_base):
    """
    Versão da Scanline Fill especializada para retângulos verticais com textura gradiente vertical.
    Entrada: Posição (x,y), Dimensões (w,h) e Cores (Topo/Base).
    """
    screen_w, screen_h = pixel_array.shape
    
    # Otimização Geométrica (Clipping)
    # Em vez de calcular interseções de arestas,
    # é feito o clamp dos valores.
    x_inicio = max(0, int(x))
    y_inicio = max(0, int(y))
    x_fim = min(screen_w, int(x + w))
    y_fim = min(screen_h, int(y + h))

    # Se estiver fora da tela, aborta
    if y_fim <= y_inicio or x_fim <= x_inicio:
        return

    # Pré-cálculo (Gradiente Vertical)
    # Calcula quanto a cor muda por linha (step).
    r1, g1, b1 = cor_topo
    r2, g2, b2 = cor_base
    
    if h > 0:
        inv_h = 1.0 / h
        dr = (r2 - r1) * inv_h
        dg = (g2 - g1) * inv_h
        db = (b2 - b1) * inv_h
    else:
        dr = dg = db = 0

    # Ajuste de cor inicial (caso o topo esteja fora da tela)
    pulo_y = y_inicio - int(y)
    cur_r = r1 + (dr * pulo_y)
    cur_g = g1 + (dg * pulo_y)
    cur_b = b1 + (db * pulo_y)

    # Loop Scanline (Vertical)
    # É um retângulo vertical, não precisa interpolar X.
    # A cor é constante na horizontal.
    for py in range(y_inicio, y_fim):
        # Cast para inteiro apenas uma vez por linha
        cor_linha = (int(cur_r), int(cur_g), int(cur_b))
        
        # Slicing
        pixel_array[x_inicio:x_fim, py] = cor_linha
        
        # Avança a cor
        cur_r += dr
        cur_g += dg
        cur_b += db

