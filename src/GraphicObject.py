from typing import Tuple, List


class GraphicObject:
    def __init__(self, name: str, obj_type: str, coordinates: List[Tuple[float, float]]):
        self.name = name
        self.type = obj_type
        self.world_coords = coordinates