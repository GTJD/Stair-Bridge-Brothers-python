class Scene(object):

    def __init__(self, game, *args, **kwargs):
        self.entities = []
        self.game = game

    def start(self):
        pass

    def stop(self):
        pass

    def reset(self):
        self.stop()
        self.start()

    def update(self, dt):
        pass

    def on_draw(self, dt):
        pass

class GameScene(Scene):
    pass

class StartScene(Scene):
    pass

class EndScene(Scene):
    pass
