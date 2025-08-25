from src.Window import Window
from typing import Tuple


class Viewport:
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int):
        self.x_min, self.y_min = x_min, y_min
        self.x_max, self.y_max = x_max, y_max

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min


def transform_coordinates(coord: Tuple[float, float], window: Window, viewport: Viewport) -> Tuple[int, int]:
    """ Fórmulas originárias da igualdade (o mesmo para Y)
    xw - xwmin          xv - xvmin
    -------------   =   -------------
    xwmax - xwmin       xvmax - xvmin
    """
    xw, yw = coord
    xv_max, yv_max = viewport.x_max, viewport.y_max
    xw_max, yw_max = window.x_max, window.y_max
    xv_min, yv_min = viewport.x_min, viewport.y_min
    xw_min, yw_min = window.x_min, window.y_min

    sx = (xw - xw_min) / (xw_max - xw_min)
    sy = (yw - yw_min) / (yw_max - yw_min)

    xv = xv_min + sx * (xv_max - xv_min)
    yv = yv_min + (1 - sy) * (yv_max - yv_min) # (1 - sy) inverte o eixo Y

    return int(xv), int(yv)

