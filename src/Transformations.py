import numpy as np
import math

def translation_matrix(dx, dy):
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1]
    ])

#TODO: adicionar possibilidade de passar o centro como param
def scaling_matrix(sx, sy):
    return np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ])

def rotation_matrix(angle):
    rad = math.radians(angle)
    cos, sin = math.cos(rad), math.sin(rad) 
    return np.array([
        [cos, -sin, 0],
        [sin, cos, 0],
        [0, 0, 1]
    ])

def build_transformation_matrix(transformations, center=(0, 0)):
    cx, cy = center
    result = np.identity(3)

    for t_type, params in transformations:
        if t_type == 'translate':
            dx, dy = params
            matrix = translation_matrix(dx, dy)
        elif t_type == 'scale':
            sx, sy = params
            # Escala em torno do centro
            matrix = np.dot(
                np.dot(translation_matrix(cx, cy), scaling_matrix(sx, sy)),
                translation_matrix(-cx, -cy)
            )
        elif t_type == 'rotate':
            angle = params
            # Rotação em torno do centro
            matrix = np.dot(
                np.dot(translation_matrix(cx, cy), rotation_matrix(angle)),
                translation_matrix(-cx, -cy)
            )
        else:
            raise ValueError(f"Tipo de transformação desconhecido: {t_type}")

        result = np.dot(matrix, result)

    return result