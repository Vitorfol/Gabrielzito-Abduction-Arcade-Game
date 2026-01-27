import math

def identity():
    """Retorna matriz identidade 3x3."""
    return [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
    ]

def translation(tx, ty):
    """Retorna matriz de translação 3x3 para deslocamento (tx, ty)."""
    return [
    [1, 0, tx],
    [0, 1, ty],
    [0, 0, 1]
    ]

def scale(sx, sy):
    """Retorna matriz de escala 3x3 para fatores (sx, sy)."""
    return [
    [sx, 0, 0],
    [0, sy, 0],
    [0, 0, 1]
    ]

def rotation(theta):
    """Retorna matriz de rotação 3x3 para ângulo theta (em radianos)."""
    c = math.cos(theta)
    s = math.sin(theta)
    
    return [
    [c, -s, 0],
    [s, c, 0],
    [0, 0, 1]
    ]
    
def create_transformation():
    """Cria matriz de transformação inicial (identidade)."""
    return identity()

def multiply_matrices(A, B):
    """Multiplica duas matrizes 3x3."""
    resultado = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(3):
        for j in range(3):
            for k in range(3):
                resultado[i][j] += A[i][k] * B[k][j]
    
    return resultado


def apply_matrix_to_point(point, matrix):
    """
    Aplica matriz de transformação 3x3 a um ponto 2D.
    
    Args:
        point: Tupla (x, y)
        matrix: Matriz 3x3 de transformação homogênea
    
    Returns:
        Tupla (new_x, new_y) com as coordenadas transformadas
    """
    x, y = point
    # Vetor homogêneo [x, y, 1]
    new_x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
    new_y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
    return (new_x, new_y)


def rotate(A, theta):
    """Aplica rotação theta à matriz de transformação A (rotaciona em torno da posição atual)."""
    R = rotation(theta)

    # posição atual (tx, ty)
    tx = A[0][2]
    ty = A[1][2]

    T = translation(-tx, -ty)
    T_inv = translation(tx, ty)

    return multiply_matrices(
        T_inv,
        multiply_matrices(
            R,
            multiply_matrices(T, A)
        )
    )

def multiply_matrix_vector(M, V):
    """
    M: matriz 3x3
    V: vetor [x, y, 1]
    retorna: [x', y', w']
    """
    return [
        M[0][0] * V[0] + M[0][1] * V[1] + M[0][2] * V[2],
        M[1][0] * V[0] + M[1][1] * V[1] + M[1][2] * V[2],
        M[2][0] * V[0] + M[2][1] * V[1] + M[2][2] * V[2],
    ]



def translate(A, tx, ty):
    """Aplica translação (tx, ty) à matriz de transformação A."""
    T = translation(tx, ty)
    return multiply_matrices(T, A)

def scale_transformation(A, sx, sy):
    """Aplica escala (sx, sy) à matriz de transformação A."""
    S = scale(sx, sy)
    return multiply_matrices(S, A)