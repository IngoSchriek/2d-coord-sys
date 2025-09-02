from typing import Tuple, List
import numpy as np

class GraphicObject:
    def __init__(self, name: str, obj_type: str, coordinates: List[Tuple[float, float]]):
        self.name = name
        self.type = obj_type
        self.world_coords = coordinates
    
    def get_points(self):
        return self.world_coords

    def set_points(self, points):
        self.world_coords = points
    
    def apply_transformation(self, matrix):
        new_points = []
        for x, y in self.world_coords:
            vec = np.array([x, y, 1])
            res = np.dot(matrix, vec)
            new_points.append((res[0], res[1]))
        self.world_coords = new_points
    
    def get_center(self):
        points = self.get_points()
        xs = [x for x, y in points]
        ys = [y for x, y in points]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    