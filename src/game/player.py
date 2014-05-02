# Represents an actual player of the game
class Player(object):

    def __init__(self, color, *args, **kwargs):
        self.bros = []
        self.color = color
        self.deaths = 0
        self.freezes = 0
        self.distance = 0

    def active_bro(self):
        if len(self.bros) > 0 and self.bros[-1].alive():
            return self.bros[-1]
        else:
            return None
