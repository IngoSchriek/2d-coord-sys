from src.GraphicObject import GraphicObject
from typing import List


class DisplayFile:
    def __init__(self):
        self.objects: List[GraphicObject] = []

    def add_object(self, obj: GraphicObject):
        self.objects.append(obj)

    def get_object_by_name(self, name: str) -> GraphicObject | None:
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None

    def clear(self):
        self.objects.clear()
