import math

class Window:
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min, self.y_min = x_min, y_min
        self.x_max, self.y_max = x_max, y_max
        self.angle = 0.0
    
    def __iter__(self):
        yield self.x_min
        yield self.y_min
        yield self.x_max
        yield self.y_max

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min

    def center(self):
        return (
            self.x_min + self.width() / 2.0,
            self.y_min + self.height() / 2.0
        )

    def move(self, dx: float, dy: float):
        self.x_min += dx
        self.x_max += dx
        self.y_min += dy
        self.y_max += dy

    def move_local(self, dx_local: float, dy_local: float):
        theta = math.radians(self.angle)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        dx_wc =  cos_t * dx_local - sin_t * dy_local
        dy_wc =  sin_t * dx_local + cos_t * dy_local
        self.move(dx_wc, dy_wc)


    def zoom(self, factor: float):
        center_x, center_y = self.center()
        new_width = self.width() * factor
        new_height = self.height() * factor

        self.x_min = center_x - new_width / 2.0
        self.x_max = center_x + new_width / 2.0
        self.y_min = center_y - new_height / 2.0
        self.y_max = center_y + new_height / 2.0

    def rotate(self, delta: float):
        self.angle = (self.angle + delta) % 360.0

    def set_angle(self, angle: float):
        self.angle = angle % 360.0