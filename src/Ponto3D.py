import numpy as np

class Ponto3D:
    def __init__(self, x, y, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.coords = np.array([self.x, self.y, self.z, 1.0])

    def apply_transform(self, matrix):
        self.coords = np.dot(matrix, self.coords)
        self.x, self.y, self.z = self.coords[0], self.coords[1], self.coords[2]

