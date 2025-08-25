from src.GraphicObject import GraphicObject
from typing import Tuple, List


class Line(GraphicObject):
    def __init__(self, name: str, coordinates: List[Tuple[float, float]]):
        super().__init__(name, "Line", coordinates)