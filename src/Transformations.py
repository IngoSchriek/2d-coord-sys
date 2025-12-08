import numpy as np
import math

def translation_matrix(dx, dy, dz):
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ])

def scaling_matrix(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])

def rotation_x_matrix(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ])

def rotation_y_matrix(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ])

def rotation_z_matrix(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def rotation_arbitrary_matrix(point, vector, angle):
    px, py, pz = point
    ux, uy, uz = vector
    u = np.array([ux, uy, uz])
    u = u / np.linalg.norm(u)
    a, b, c = u
    
    rad = math.radians(angle)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    one_minus_cos = 1 - cos_t

    rot = np.array([
        [a*a + (1-a*a)*cos_t, a*b*one_minus_cos - c*sin_t, a*c*one_minus_cos + b*sin_t, 0],
        [a*b*one_minus_cos + c*sin_t, b*b + (1-b*b)*cos_t, b*c*one_minus_cos - a*sin_t, 0],
        [a*c*one_minus_cos - b*sin_t, b*c*one_minus_cos + a*sin_t, c*c + (1-c*c)*cos_t, 0],
        [0, 0, 0, 1]
    ])
    
    t_origin = translation_matrix(-px, -py, -pz)
    t_back = translation_matrix(px, py, pz)
    
    return t_back @ rot @ t_origin

def view_transform_matrix(vrp, vpn, vup):
    vrp = np.array(vrp, dtype=float)
    vpn = np.array(vpn, dtype=float)
    vup = np.array(vup, dtype=float)

    n = vpn / np.linalg.norm(vpn)
    u = np.cross(vup, n)
    norm_u = np.linalg.norm(u)
    if norm_u < 1e-9:
        u = np.array([1.0, 0.0, 0.0])
    else:
        u = u / norm_u
    v = np.cross(n, u)
    v = v / np.linalg.norm(v)

    R = np.array([
        [u[0], u[1], u[2], 0],
        [v[0], v[1], v[2], 0],
        [n[0], n[1], n[2], 0],
        [0, 0, 0, 1]
    ])

    T = translation_matrix(-vrp[0], -vrp[1], -vrp[2])
    return R @ T

def perspective_matrix(d):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/d, 1]
    ])
