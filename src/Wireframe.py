from src.GraphicObject import GraphicObject
from typing import List, Tuple


class Wireframe(GraphicObject):
    def __init__(self, name: str, coordinates: List[Tuple[float, float]]):
        super().__init__(name, "Wireframe", coordinates)