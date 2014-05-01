import entity

# A goal that players reach at the end of a Section
class CheckPoint(entity.Entity):

    def __init__(self, *args, **kwargs):
        self.complete = False
