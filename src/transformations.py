import math

def identity():
    return [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
    ]

def translation(tx, ty):
    return [
    [1, 0, tx],
    [0, 1, ty],
    [0, 0, 1]
    ]

def scale(sx, sy):
    return [
    [sx, 0, 0],
    [0, sy, 0],
    [0, 0, 1]
    ]

def rotation(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    
    return [
    [c, -s, 0],
    [s, c, 0],
    [0, 0, 1]
    ]
    
def create_transformation():
    return identity()

def multiply_matrices(A, B):
    resultado = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    for i in range(3):
        for j in range(3):
            for k in range(3):
                resultado[i][j] += A[i][k] * B[k][j]
    
    return resultado

def rotate(A, theta):
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


def translate(A, tx, ty):
    T = translation(tx, ty)
    return multiply_matrices(T, A)

def scale_transformation(A, sx, sy):
    S = scale(sx, sy)
    return multiply_matrices(S, A)