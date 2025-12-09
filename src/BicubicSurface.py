import numpy as np
from src.Ponto3D import Ponto3D
from src.Objeto3D import Objeto3D
from src.Transformations import translation_matrix

class BicubicSurface(Objeto3D):
    def __init__(self, name: str):
        super().__init__(name)
        self.type = "BicubicSurface"
        self.patches = []
        self.steps = 10

    def add_patch(self, points_16: list):
        if len(points_16) != 16:
            raise ValueError("Patch incomplete")
        self.patches.append(points_16)
        self.generate_mesh()

    def generate_mesh(self):
        self.segments = []
        Mb = np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  3,  0,  0],
            [ 1,  0,  0,  0]
        ])
        
        for patch in self.patches:
            coords_x = np.array([p.x for p in patch]).reshape(4, 4)
            coords_y = np.array([p.y for p in patch]).reshape(4, 4)
            coords_z = np.array([p.z for p in patch]).reshape(4, 4)
            
            Cx = Mb @ coords_x @ Mb.T
            Cy = Mb @ coords_y @ Mb.T
            Cz = Mb @ coords_z @ Mb.T
            
            def eval_surface(s, t):
                S = np.array([s**3, s**2, s, 1])
                T = np.array([t**3, t**2, t, 1])
                x = S @ Cx @ T.T
                y = S @ Cy @ T.T
                z = S @ Cz @ T.T
                return Ponto3D(x, y, z)

            for i in range(self.steps + 1):
                s = i / self.steps
                prev_p = eval_surface(s, 0)
                for j in range(1, self.steps + 1):
                    t = j / self.steps
                    curr_p = eval_surface(s, t)
                    self.add_segment(prev_p, curr_p)
                    prev_p = curr_p
            
            for j in range(self.steps + 1):
                t = j / self.steps
                prev_p = eval_surface(0, t)
                for i in range(1, self.steps + 1):
                    s = i / self.steps
                    curr_p = eval_surface(s, t)
                    self.add_segment(prev_p, curr_p)
                    prev_p = curr_p

    def apply_transformation(self, matrix):
        points_to_transform = set()
        for patch in self.patches:
            for p in patch:
                points_to_transform.add(p)
        
        for p in points_to_transform:
            p.apply_transform(matrix)
        
        self.generate_mesh()

    def get_center(self):
        all_points = []
        for patch in self.patches:
            all_points.extend(patch)
        
        if not all_points: return (0,0,0)
        
        sx = sum(p.x for p in all_points)
        sy = sum(p.y for p in all_points)
        sz = sum(p.z for p in all_points)
        n = len(all_points)
        return (sx/n, sy/n, sz/n)
    
    def transform_to_center(self, matrix):
        cx, cy, cz = self.get_center()
        t_origin = translation_matrix(-cx, -cy, -cz)
        t_back = translation_matrix(cx, cy, cz)
        full_matrix = t_back @ matrix @ t_origin
        self.apply_transformation(full_matrix)
