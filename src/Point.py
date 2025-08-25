from typing import List, Tuple
from src.GraphicObject import GraphicObject

class Point(GraphicObject):
    def __init__(self, name: str, coordinates: List[Tuple[float, float]]):
        super().__init__(name, "Point", coordinates)