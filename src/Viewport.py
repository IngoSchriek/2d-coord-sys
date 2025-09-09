from src.Window import Window
from typing import Tuple
import math

class Viewport:
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int):
        self.x_min, self.y_min = x_min, y_min
        self.x_max, self.y_max = x_max, y_max

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min


def transform_coordinates(point, window, viewport) -> tuple[int, int]:
    u, v = wc_to_ppc(point, window)
    return ppc_to_screen(u, v, viewport)

def wc_to_ppc(point, window) -> tuple[float, float]:
    #tira centro; rotaciona por -theta; normaliza para [-w/2,+w/2]->[0,1].
    xw, yw = point
    cx, cy = window.center()
    theta = math.radians(window.angle)
    cos_t, sin_t = math.cos(-theta), math.sin(-theta)

    xr =  cos_t * (xw - cx) - sin_t * (yw - cy)
    yr =  sin_t * (xw - cx) + cos_t * (yw - cy)

    u = (xr / window.width())  + 0.5
    v = (yr / window.height()) + 0.5
    return u, v

def ppc_to_screen(u, v, viewport: Viewport) -> tuple[int, int]:
    x = viewport.x_min + u * viewport.width()
    y = viewport.y_max - v * viewport.height()  # inverte v
    return int(round(x)), int(round(y))