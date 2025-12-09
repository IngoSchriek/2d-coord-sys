from src.Ponto3D import Ponto3D
from src.Transformations import translation_matrix

class Objeto3D:
    def __init__(self, name):
        self.name = name
        self.type = "Objeto3D"
        self.segments = []

    def add_segment(self, p1: Ponto3D, p2: Ponto3D):
        self.segments.append((p1, p2))

    def apply_transformation(self, matrix):
        points = set()
        for p1, p2 in self.segments:
            points.add(p1)
            points.add(p2)
        for p in points:
            p.apply_transform(matrix)

    def get_center(self):
        points = set()
        for p1, p2 in self.segments:
            points.add(p1)
            points.add(p2)
        if not points: return (0,0,0)
        sx = sum(p.x for p in points)
        sy = sum(p.y for p in points)
        sz = sum(p.z for p in points)
        n = len(points)
        return (sx/n, sy/n, sz/n)

    def transform_to_center(self, matrix):
        cx, cy, cz = self.get_center()
        t_origin = translation_matrix(-cx, -cy, -cz)
        t_back = translation_matrix(cx, cy, cz)
        full_matrix = t_back @ matrix @ t_origin
        self.apply_transformation(full_matrix)
