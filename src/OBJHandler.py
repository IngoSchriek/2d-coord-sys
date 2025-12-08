from src.DisplayFile import DisplayFile
from src.Point import Point
from src.Line import Line
from src.Objeto3D import Objeto3D
from src.Ponto3D import Ponto3D
from typing import List

class OBJHandler:
    @staticmethod
    def save_to_obj(display_file: DisplayFile, filename: str):
        with open(filename, 'w') as f:
            f.write("# OBJ exportado\n\n")
            vertex_offset = 1
            for obj in display_file.objects:
                if isinstance(obj, Objeto3D):
                    unique_points = []
                    point_map = {} 
                    for p1, p2 in obj.segments:
                        if p1 not in point_map:
                            point_map[p1] = len(unique_points) + 1
                            unique_points.append(p1)
                        if p2 not in point_map:
                            point_map[p2] = len(unique_points) + 1
                            unique_points.append(p2)
                    
                    f.write(f"o {obj.name}\n")
                    for p in unique_points:
                        f.write(f"v {p.x} {p.y} {p.z}\n")
                    
                    for p1, p2 in obj.segments:
                        idx1 = vertex_offset + point_map[p1] - 1
                        idx2 = vertex_offset + point_map[p2] - 1
                        f.write(f"l {idx1} {idx2}\n")
                    
                    vertex_offset += len(unique_points)
                    f.write("\n")
                
                # Suporte legado para objetos 2D
                elif hasattr(obj, 'world_coords'):
                    f.write(f"o {obj.name}\n")
                    for x, y in obj.world_coords:
                        f.write(f"v {x} {y} 0.0\n")
                    if obj.type == "Line":
                        f.write(f"l {vertex_offset} {vertex_offset + 1}\n")
                    elif obj.type == "Wireframe":
                        for i in range(len(obj.world_coords)):
                            s = vertex_offset + i
                            e = vertex_offset + ((i + 1) % len(obj.world_coords))
                            f.write(f"l {s} {e}\n")
                    vertex_offset += len(obj.world_coords)
                    f.write("\n")

    @staticmethod
    def load_from_obj(filename: str) -> DisplayFile:
        display_file = DisplayFile()
        vertices = [] 
        
        with open(filename, 'r') as f:
            current_name = None
            current_lines = []
            
            for line in f:
                parts = line.strip().split()
                if not parts: continue
                
                if parts[0] == 'v':
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3]) if len(parts) > 3 else 0.0
                    vertices.append(Ponto3D(x, y, z))
                
                elif parts[0] == 'o':
                    if current_name and current_lines:
                        OBJHandler._create_object3d(display_file, current_name, vertices, current_lines)
                    current_name = parts[1]
                    current_lines = []

                elif parts[0] == 'l':
                    indices = [int(p.split('/')[0]) for p in parts[1:]]
                    for i in range(len(indices) - 1):
                        current_lines.append((indices[i], indices[i+1]))
                    if len(indices) > 2:
                         current_lines.append((indices[-1], indices[0]))

            if current_name and current_lines:
                OBJHandler._create_object3d(display_file, current_name, vertices, current_lines)
        
        return display_file

    @staticmethod
    def _create_object3d(display_file, name, all_vertices, lines_indices):
        obj = Objeto3D(name)
        for idx1, idx2 in lines_indices:
            p1 = all_vertices[idx1 - 1]
            p2 = all_vertices[idx2 - 1]
            new_p1 = Ponto3D(p1.x, p1.y, p1.z)
            new_p2 = Ponto3D(p2.x, p2.y, p2.z)
            obj.add_segment(new_p1, new_p2)
        display_file.add_object(obj)
