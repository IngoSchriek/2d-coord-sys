from src.GraphicObject import GraphicObject
from typing import List, Tuple

class BezierCurve(GraphicObject):
    def __init__(self, name: str, coordinates: List[Tuple[float, float]]):
        super().__init__(name, "Bezier Curve", coordinates)

    def get_segments(self):
        if len(self.world_coords) < 4:
            return []
        
        segments = []
        segments.append(self.world_coords[0:4])

        for i in range(4, len(self.world_coords), 3):
            if (i + 2) < len(self.world_coords):
                segments.append([self.world_coords[i-1], self.world_coords[i], self.world_coords[i+1], self.world_coords[i+2]])
            
        return segments