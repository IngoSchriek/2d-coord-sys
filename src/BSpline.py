from src.GraphicObject import GraphicObject
from typing import List, Tuple
import numpy as np

class BSpline(GraphicObject):
    def __init__(self, name: str, coordinates: List[Tuple[float, float]]):
        super().__init__(name, "BSpline", coordinates)
        self.M_bs = (1.0 / 6.0) * np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ])

    def generate_points(self, num_steps: int = 10) -> List[Tuple[float, float]]:
        points = self.world_coords
        n = len(points)
        
        if n < 4:
            return []

        curve_points = []
        delta = 1.0 / num_steps
        
        E = np.array([
            [0,           0,           0,       1],
            [delta**3,    delta**2,    delta,   0],
            [6*delta**3,  2*delta**2,  0,       0],
            [6*delta**3,  0,           0,       0]
        ])

        for i in range(n - 3):
            Gx = np.array([p[0] for p in points[i:i+4]])
            Gy = np.array([p[1] for p in points[i:i+4]])

            Cx = self.M_bs @ Gx
            Cy = self.M_bs @ Gy

            init_x = E @ Cx
            init_y = E @ Cy

            x, dx, d2x, d3x = init_x
            y, dy, d2y, d3y = init_y

            curve_points.append((x, y))
            for _ in range(num_steps):
                x += dx
                dx += d2x
                d2x += d3x

                y += dy
                dy += d2y
                d2y += d3y
                
                curve_points.append((x, y))

        return curve_points
