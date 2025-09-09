from src.DisplayFile import DisplayFile
from src.Point import Point
from src.Line import Line
from src.Wireframe import Wireframe
from typing import List, Tuple

class OBJHandler:
    @staticmethod
    def save_to_obj(display_file: DisplayFile, filename: str):
        with open(filename, 'w') as f:
            f.write("# Arquivo OBJ gerado pelo Sistema Gráfico Interativo\n")
            f.write("# Desenvolvido por [Seu Nome]\n\n")

            vertex_offset = 1  # Índices em .obj começam em 1
            for obj in display_file.objects:
                if not obj.world_coords:
                    continue
                
                f.write(f"o {obj.name}\n")
                
                # Escreve os vértices do objeto
                for x, y in obj.world_coords:
                    f.write(f"v {x} {y} 0.0\n")
                
                # Escreve a conectividade (arestas/linhas)
                if obj.type == "Line":
                    f.write(f"l {vertex_offset} {vertex_offset + 1}\n")
                elif obj.type == "Wireframe":
                    num_vertices = len(obj.world_coords)
                    for i in range(num_vertices):
                        start_index = vertex_offset + i
                        end_index = vertex_offset + ((i + 1) % num_vertices)
                        f.write(f"l {start_index} {end_index}\n")
                
                vertex_offset += len(obj.world_coords)
                f.write("\n")

    @staticmethod
    def load_from_obj(filename: str) -> DisplayFile:
        display_file = DisplayFile()
        vertices: List[Tuple[float, float]] = []
        
        with open(filename, 'r') as f:
            current_object_name = None
            object_coords: List[Tuple[float, float]] = []
            
            object_lines = {}

            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                
                command = parts[0]

                if command == 'v':
                    # Armazena todos os vértices do arquivo
                    x, y = float(parts[1]), float(parts[2])
                    vertices.append((x, y))
                
                elif command == 'o':
                    # Se encontrarmos um novo objeto, processamos o anterior
                    if current_object_name and object_coords:
                        OBJHandler._create_object(display_file, current_object_name, object_coords, object_lines.get(current_object_name, []))
                    
                    current_object_name = parts[1]
                    object_coords = []
                    object_lines[current_object_name] = []

                elif command == 'l':
                    if current_object_name:
                        # Armazena os índices dos vértices que formam uma linha
                        line_indices = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                        object_lines[current_object_name].append(line_indices)
            
            # Processa o último objeto do arquivo
            if current_object_name:
                 OBJHandler._create_object(display_file, current_object_name, object_coords, object_lines.get(current_object_name, []))
        
        # Reconstrói as coordenadas dos objetos a partir das linhas lidas
        for obj in display_file.objects:
            if obj.name in object_lines:
                obj_indices = set()
                for line_def in object_lines[obj.name]:
                    for index in line_def:
                        obj_indices.add(index)
                
                # Garante a ordem original dos vértices
                sorted_indices = sorted(list(obj_indices))
                obj.world_coords = [vertices[i] for i in sorted_indices]

        return display_file

    @staticmethod
    def _create_object(display_file, name, coords, lines):
        num_vertices = len(coords)
        num_lines = len(lines)

        obj = None
        if num_lines == 0 and num_vertices == 1:
            obj = Point(name, coords)
        elif num_lines == 1 and num_vertices == 2:
            obj = Line(name, coords)
        else:
            obj = Wireframe(name, coords)
        
        if obj:
            display_file.add_object(obj)