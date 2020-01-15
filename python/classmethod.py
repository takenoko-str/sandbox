class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @classmethod
    def polar(cls, r, theta):
        return cls(r * cos(theta),
                   r * sin(theta))

point = Point.polar(r=13, theta=22.6)