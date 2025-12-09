import numpy as np
from src.Ponto3D import Ponto3D
from src.Objeto3D import Objeto3D
from src.Transformations import translation_matrix

class BSplineSurface(Objeto3D):
    def __init__(self, name: str):
        super().__init__(name)
        self.type = "BSpline Surface"
        self.control_points = []
        self.steps = 10

    def set_control_points(self, matrix_points: list):
        rows = len(matrix_points)
        if rows < 4:
            raise ValueError(f"Grid must be at least 4x4. Rows: {rows}")
        cols = len(matrix_points[0])
        if cols < 4:
            raise ValueError(f"Grid must be at least 4x4. Cols: {cols}")
        
        self.control_points = matrix_points
        self.generate_mesh()

    def generate_mesh(self):
        self.segments = []
        
        Mbs = np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ]) * (1/6)

        rows = len(self.control_points)
        cols = len(self.control_points[0])

        for r in range(rows - 3):
            for c in range(cols - 3):
                local_patch = []
                for i in range(4):
                    local_patch.append(self.control_points[r+i][c:c+4])
                
                self.draw_patch_fwd_diff(local_patch, Mbs)

    def draw_patch_fwd_diff(self, patch, M):
        Gx = np.array([[p.x for p in row] for row in patch])
        Gy = np.array([[p.y for p in row] for row in patch])
        Gz = np.array([[p.z for p in row] for row in patch])

        Cx = M @ Gx @ M.T
        Cy = M @ Gy @ M.T
        Cz = M @ Gz @ M.T

        d = 1.0 / self.steps
        d2 = d * d
        d3 = d * d * d
        
        E = np.array([
            [0,       0,      0,      1],
            [d3,      d2,     d,      0],
            [6*d3,    2*d2,   0,      0],
            [6*d3,    0,      0,      0]
        ])

        for i in range(self.steps + 1):
            s = i / self.steps
            S_vec = np.array([s**3, s**2, s, 1])
            
            coeffs_x = S_vec @ Cx 
            coeffs_y = S_vec @ Cy
            coeffs_z = S_vec @ Cz

            init_x = E @ coeffs_x
            init_y = E @ coeffs_y
            init_z = E @ coeffs_z

            self.plot_curve_fwd(init_x, init_y, init_z)

        for i in range(self.steps + 1):
            t = i / self.steps
            T_vec = np.array([t**3, t**2, t, 1])
            
            coeffs_x = Cx @ T_vec
            coeffs_y = Cy @ T_vec
            coeffs_z = Cz @ T_vec

            init_x = E @ coeffs_x
            init_y = E @ coeffs_y
            init_z = E @ coeffs_z

            self.plot_curve_fwd(init_x, init_y, init_z)

    def plot_curve_fwd(self, ix, iy, iz):
        x, dx, d2x, d3x = ix
        y, dy, d2y, d3y = iy
        z, dz, d2z, d3z = iz

        prev_p = Ponto3D(x, y, z)

        for _ in range(self.steps):
            x += dx; dx += d2x; d2x += d3x
            y += dy; dy += d2y; d2y += d3y
            z += dz; dz += d2z; d2z += d3z

            curr_p = Ponto3D(x, y, z)
            self.add_segment(prev_p, curr_p)
            prev_p = curr_p

    def apply_transformation(self, matrix):
        flat_points = set()
        for row in self.control_points:
            for p in row:
                flat_points.add(p)
        
        for p in flat_points:
            p.apply_transform(matrix)
        
        self.generate_mesh()

    def get_center(self):
        if not self.control_points: return (0,0,0)
        
        sum_x = sum_y = sum_z = 0
        count = 0
        for row in self.control_points:
            for p in row:
                sum_x += p.x; sum_y += p.y; sum_z += p.z
                count += 1
        
        return (sum_x/count, sum_y/count, sum_z/count)

    def transform_to_center(self, matrix):
        cx, cy, cz = self.get_center()
        t_origin = translation_matrix(-cx, -cy, -cz)
        t_back = translation_matrix(cx, cy, cz)
        full_matrix = t_back @ matrix @ t_origin
        self.apply_transformation(full_matrix)
