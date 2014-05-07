import pyglet
import rabbyt
import game

class Game(pyglet.window.Window):

    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 480
    WINDOW_DIM = (WINDOW_WIDTH, WINDOW_HEIGHT)
    WINDOW_FULLSCREEN = False

    KEY_BINDINGS = {
            'reset': pyglet.window.key.R,
            'fullscreen': pyglet.window.key.F11
            }

    def __init__(self, *args, **kwargs):
        # set window size
        if Game.WINDOW_FULLSCREEN:
            kwargs['fullscreen'] = True
        else:
            kwargs['width'] = Game.WINDOW_WIDTH
            kwargs['height'] = Game.WINDOW_HEIGHT

        super(Game, self).__init__( *args, **kwargs)

        # prevent resize
        self.resizeable = False
        self.set_minimum_size(self.width, self.height)

        self.set_mouse_visible = False
        
        # rabbyt set up
        rabbyt.set_default_attribs()

        # game scenes, these include the main game and the supporting menu scenes
        self._current_scene = None

    def static_projection(self):
        return (0, self.height, self.width, 0)

    def start(self):
        # track fps
        self.fps_display = pyglet.clock.ClockDisplay()

        # Create and start the first scene
        self.current_scene = game.scene.GameScene(self)
        self.current_scene.start()

        # start the game loop
        pyglet.app.run()

    def stop(self):
        if self.current_scene is not None:
            self.current_scene.stop()

        # stop the game loop
        pyglet.app.exit()

    def reset(self):
        self.stop()
        self.start()

    def update(self, dt):
        # update the current scene
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def on_draw(self):
        rabbyt.clear()
        # Draw the current scene
        if self.current_scene is not None:
            self.current_scene.on_draw()
        # Draw fps
        rabbyt.set_viewport((self.width, self.height), projection=self.static_projection())
        self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        # Global
        if symbol == Game.KEY_BINDINGS['reset']:
            self.reset()
        elif symbol == Game.KEY_BINDINGS['fullscreen']:
            self.toggle_fullscreen()
        # have the current scene handle remaining inputs
        elif self.current_scene is not None:
            self.current_scene.on_key_press(symbol, modifiers)

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)
        if not self.fullscreen:
            self.set_size(Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT)

    def on_key_release(self, symbol, modifiers):
        if self.current_scene is not None:
            self.current_scene.on_key_release(symbol, modifiers)

    def on_resize(self, width, height):
        if self.current_scene is not None:
            self.current_scene.on_resize(width, height)

    @property
    def current_scene(self):
        return self._current_scene

    @current_scene.setter
    def current_scene(self, scene):
        # stop the old scene
        if self.current_scene is not None:
            self.current_scene.stop()

        self._current_scene = scene

PROFILE = False

def main():
    g = Game()
    g.start()

# Start game when running this file 
if __name__ == '__main__':
    if PROFILE:
        import cProfile
        cProfile.run('main()')
    else:
        main()
