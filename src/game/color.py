# A Bro's color
class Color(object):

    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def tup(self):
        r = int(self.red * 255)
        g = int(self.green * 255)
        b = int(self.blue * 255)
        return (r, g, b)

    def invert(self):
        r = 1 - self.red
        g = 1 - self.green
        b = 1 - self.blue
        return Color(r, g, b)

    def fade(self, fade):
        r = fade + self.red
        g = fade + self.green
        b = fade + self.blue
        return Color(r, g, b)

RED = Color(1, 0.25, 0.25)
BLUE = Color(0.25, 0.25, 1)
YELLOW = Color(1, 1, 0.25)
