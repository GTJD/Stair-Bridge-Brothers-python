import pyglet
import pymunk
import rabbyt

from OpenGL.GL import *

from collections import deque

#from game import resources, color, section
#from game import player as p
import game

# Add tuple element-wise
def addt(a, b):
    return (map(sum,zip(a,b)))

class Game(pyglet.window.Window):

    BACKGROUND = pyglet.image.TileableTexture.create_for_image(game.resources.background)

    COLORS = [game.color.RED, game.color.BLUE, game.color.YELLOW]

    GRAVITY = (0.0, -500.0)
    PHYSICS_FRAMERATE = 1.0 / 80

    DEATH_Y = -80

    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 480
    WINDOW_DIM = (WINDOW_WIDTH, WINDOW_HEIGHT)

    SCROLL_RATE = 6
    SCROLL_DELAY = 2
    DROP_LINE_START = -150

    START_PROJECTION_X = -200
    START_PROJECTION_Y = -32
    START_PROJECTION = (
            START_PROJECTION_X, 
            WINDOW_HEIGHT + START_PROJECTION_Y, 
            WINDOW_WIDTH + START_PROJECTION_X, 
            START_PROJECTION_Y)

    STATIC_PROJECTION = (0, WINDOW_HEIGHT, WINDOW_WIDTH, 0)

    PROJECTION_SCROLL = (SCROLL_RATE, 0, SCROLL_RATE, 0) 

    SCORE_FONT = 'monospace'
    SCORE_SIZE = 36
    SCORE_OFFSET = 50
    SCORE_SPACING = (WINDOW_WIDTH / 3)
    SCORE_Y = WINDOW_HEIGHT - 100

    POPULATE_PADDING = 50

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        
        # Window settings
        self.width, self.height = Game.WINDOW_DIM

        # rabbyt set up
        rabbyt.set_default_attribs()

        self.start()

    def start(self):

        # Create players
        self.players = []
        self.score_labels = []
        for i, color in enumerate(Game.COLORS):
            player = game.player.Player(color=color)
            self.players.append(player)
            # Score Labels
            label = pyglet.text.Label('0', 
                        #font_name = Game.SCORE_FONT, 
                        font_size = Game.SCORE_SIZE,
                        bold = True,
                        color = color.tup(),
                        x = i * Game.SCORE_SPACING + Game.SCORE_OFFSET,
                        y = Game.SCORE_Y)
            self.score_labels.append(label)


        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = Game.GRAVITY

        # Create first section
        self.entities = []
        self.sections = deque()
        self.current_distance = 0
        self.push_section()

        # Create entities
        self.bros = []
        for i, player in enumerate(self.players):
            self.add_bro(player, y=(i+2)*50)

        # track fps
        self.fps_display = pyglet.clock.ClockDisplay()

        # slowly panning camera
        self.camera = Game.START_PROJECTION

        # Game state
        self.scroll_delay = Game.SCROLL_DELAY
        self.drop_line = Game.DROP_LINE_START

        # Schedule updating game
        pyglet.clock.schedule(rabbyt.add_time)
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update_physics, Game.PHYSICS_FRAMERATE)

        # start pyglet
        pyglet.app.run()

    def stop(self):
        pyglet.clock.unschedule(rabbyt.add_time)
        pyglet.clock.unschedule(self.update)
        pyglet.clock.unschedule(self.update_physics)

    def reset(self):
        self.stop()
        self.start()

    def update(self, dt):

        # Scroll viewport or decrement scroll delay
        if self.scroll_delay > 0:
            self.scroll_delay -= dt
            dscroll = max(0, dt - self.scroll_delay)
        else:
            dscroll = dt

        dcamera = Game.get_scroll(dscroll) 
        self.camera = addt(self.camera, dcamera)

        self.drop_line += dscroll * Game.SCROLL_RATE

        # update entities
        for entity in self.entities:
            entity.update(dt)

        # Kill bros that have fallen
        for bro in self.bros:
            if bro.y < Game.DEATH_Y:
                self.kill_bro(bro)
            elif bro.x < self.drop_line:
                bro.drop()

        for tile in self.sections[0].tiles:
            # Remove fallen tiles
            if tile.y < Game.DEATH_Y:
                self.sections[0].tiles.remove(tile)
                self.entities.remove(tile)
            # Drop tiles behind drop line
            elif tile.x < self.drop_line:
                tile.drop()

        # delete empty sections
        if len(self.sections[0].tiles) == 0:
            self.pop_section()

        # update score labels
        for player, label in zip(self.players, self.score_labels):
            label.text = str(player.distance)

        # add sections 
        while self.current_distance * game.tile.Tile.SIZE < self.populate_distance():
            self.push_section()

    def update_physics(self, dt):
        self.space.step(dt)

    def camera_distance(self):
        return self.camera[2]

    def populate_distance(self):
        return self.camera_distance() + Game.POPULATE_PADDING

    @staticmethod
    def get_scroll(dt):
        return (map(lambda x: x * dt, Game.PROJECTION_SCROLL))

    def on_draw(self):
        rabbyt.clear()

        # Draw background
        rabbyt.set_viewport(Game.WINDOW_DIM, projection=Game.STATIC_PROJECTION)
        # reset opengl draw colour
        glColor(255, 255, 255, 1)
        Game.BACKGROUND.blit_tiled(0, 0, 0, self.width, self.height)

        # Draw transformed sprites
        rabbyt.set_viewport(Game.WINDOW_DIM, projection=self.camera)
        rabbyt.render_unsorted(self.entities)

        # Draw static sprites
        rabbyt.set_viewport(Game.WINDOW_DIM, projection=Game.STATIC_PROJECTION)
        self.fps_display.draw()
        for label in self.score_labels:
            label.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            bro = self.get_bro(0)
            if bro: bro.jump()
        elif symbol == pyglet.window.key.LEFT:
            bro = self.get_bro(0)
            if bro: bro.move_left()
        elif symbol == pyglet.window.key.RIGHT:
            bro = self.get_bro(0)
            if bro: bro.move_right()
        elif symbol == pyglet.window.key.F:
            bro = self.get_bro(0)
            if bro: 
                bro.freeze()
                self.add_bro(bro.player)
        elif symbol == pyglet.window.key.S:
            self.push_section()
        elif symbol == pyglet.window.key.DELETE:
            self.pop_section()
        elif symbol == pyglet.window.key.R:
            self.reset()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            bro = self.get_bro(0)
            if bro: bro.stop_left()
        elif symbol == pyglet.window.key.RIGHT:
            bro = self.get_bro(0)
            if bro: bro.stop_right()

    def get_bro(self, num):
        p = self.players[0]
        return p.active_bro()

    def add_bro(self, player, y=100):
        x = self.sections[0].first_tile_offset()
        bro = game.bro.Bro(player, self.space, x=x, y=y)
        self.entities.append(bro)
        self.bros.append(bro)

    def kill_bro(self, bro):
        bro.die()
        self.entities.remove(bro)
        self.bros.remove(bro)
        if not bro.frozen:
            self.add_bro(bro.player)

    def push_section(self):
        section = game.section.Section(self.current_distance, self.space)
        self.sections.append(section)
        self.entities += section.tiles
        self.current_distance += section.length

    def pop_section(self):
        section = self.sections.popleft()
        for tile in section.tiles:
            self.entities.remove(tile)
            self.space.remove(tile.pymunk_shape)

    def remove_section(self, section):
        self.sections.remove(section)

# Start game when running this file 
if __name__ == '__main__':
    game = Game()
    game.start()
    pyglet.app.run()
