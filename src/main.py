import pyglet
import pymunk
import rabbyt

import random

from collections import deque
from math import degrees

from game import resources

## Functions
def addt(a, b):
    return (map(sum,zip(a,b)))

## Classes ##

# Represents an actual player of the game
class Player(object):

    def __init__(self, color, *args, **kwargs):
        self.score = 0
        self.bros = []
        self.color = color
        self.deaths = 0
        self.freezes = 0
        self.distance = 0

    def active_bro(self):
        if len(self.bros) > 0:
            return self.bros[-1]
        else:
            return None

# An object with a sprite and presence in the physucs space
class Entity(rabbyt.Sprite):
    pass

# An avatar controlled by a Player
class Bro(Entity):

    MASS = 10
    FRICTION = 0.5
    SIZE = 32 

    JUMP_VECTOR = (0, 2000)
    SPEED = 100

    FROZEN_OPACITY = 0.8
    FREEZE_FADE = 0.3

    @property
    def color(self):
        self._color 

    @color.setter
    def color(self, val):
        self._color = val
        self.red = val.red
        self.green = val.green
        self.blue = val.blue

    @color.deleter
    def color(self):
        del self._color
        self.red = 1
        self.green = 1
        self.blue = 1

    def __init__(self, player, space, x=0, y=100, *args, **kwargs):
        super(Bro, self).__init__(texture=resources.box)
        self.player = player
        self.color = player.color
        self.dead = False
        self.frozen = False
        self.space = space
        self.player.bros.append(self)

        # Physics setup
        angle = 0
        mass = Bro.MASS
        width = Bro.SIZE
        height = Bro.SIZE
        moment = pymunk.moment_for_box(mass, width, height)
        body = pymunk.Body(mass, moment)
        hw = Bro.SIZE // 2
        vs = [(-hw, hw), (hw, hw), (hw, -hw), (-hw, -hw)]
        shape = pymunk.Poly(body, vs)
        shape.friction = Bro.FRICTION
        body.position = x, y
        body.angle = angle

        space.add(body, shape)

        self.pymunk_shape = shape
        self.pymunk_body = body

        # Model state
        self.jumping = False
        self.moving_left = False
        self.moving_right = False

    def update(self, dt):
        self.x = self.pymunk_body.position.x
        self.y = self.pymunk_body.position.y
        self.rot = degrees(self.pymunk_body.angle)

        if self.moving_left:
            target_velocity = -Bro.SPEED
        elif self.moving_right:
            target_velocity = Bro.SPEED
        else:
            target_velocity = 0

        self.pymunk_body.velocity.x = target_velocity

        # update player distance
        self.player.distance = int(max(self.x, self.player.distance))

    def freeze(self):
        self.frozen = True
        self.player.freezes += 1

        # make sprite transparent
        #self.alpha = Bro.FROZEN_OPACITY
        self.red += Bro.FREEZE_FADE
        self.green += Bro.FREEZE_FADE 
        self.blue += Bro.FREEZE_FADE

        # remove body from physics space and make it static
        self.space.remove(self.pymunk_body)
        self.pymunk_body.velocity = 0, 0
        self.pymunk_body.angular_velocity = 0
        self.pymunk_body.mass = pymunk.inf
        self.pymunk_body.moment = pymunk.inf

    def die(self):
        self.dead = True
        self.player.deaths += 1
        # remove body from physics space
        self.space.remove(self.pymunk_body, self.pymunk_shape)

    def jump(self):
        #if not self.jumping:
        self.pymunk_body.apply_impulse(Bro.JUMP_VECTOR, (0, 0))
            #self.jumping = True

    def move_right(self):
        self.moving_right = True
        self.moving_left = False

    def move_left(self):
        self.moving_left = True
        self.moving_right = False

    def stop_right(self):
        self.moving_right = False

    def stop_left(self):
        self.moving_left = False

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
        return (r, g, b, 255)

Color.RED = Color(1, 0.25, 0.25)
Color.BLUE = Color(0.25, 0.25, 1)
Color.YELLOW = Color(1, 1, 0.25)

# A single tile making up the world
class Tile(Entity):

    FRICTION = 0.5
    SIZE = 32

    WHITE_RATIO = 0.5

    BRIGHTNESS_MIN = 0.7
    BRIGHTNESS_RANGE = 1.0 - BRIGHTNESS_MIN

    def __init__(self, x, y, space, *args, **kwargs):
        self.space = space
        super(Tile, self).__init__(texture=resources.box)

        # Physics setup
        x *= Tile.SIZE
        y *= Tile.SIZE
        angle = 0
        width = Tile.SIZE
        height = Tile.SIZE
        body = pymunk.Body()
        hw = Tile.SIZE // 2
        vs = [(-hw, hw), (hw, hw), (hw, -hw), (-hw, -hw)]
        shape = pymunk.Poly(body, vs)
        shape.friction = Tile.FRICTION
        body.position = x, y
        body.angle = angle

        # random colour
        if random.random() < Tile.WHITE_RATIO:
            brightness = random.random() % Tile.BRIGHTNESS_RANGE + Tile.BRIGHTNESS_MIN
            self.red = brightness
            self.green = brightness
            self.blue = brightness

        space.add(shape)

        self.pymunk_shape = shape
        self.pymunk_body = body

        self.x = self.pymunk_body.position.x
        self.y = self.pymunk_body.position.y

    def update(self, dt):
        pass

# A goal that players reach at the end of a Section
class CheckPoint(rabbyt.sprites.Sprite):

    def __init__(self, *args, **kwargs):
        self.complete = False

# A collection of Tiles with a CheckPoint at the end
class Section(object):

    TILE_SETS = [
        [
            [0,0,0,1,0,0,0,0,0,0,0],
            [0,0,1,1,1,0,0,0,0,0,0],
            [1,1,1,1,1,0,0,0,0,1,1],
        ],
        [
            [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1],
        ]
    ]

    def __init__(self, offset, space, *args, **kwargs):
        self.offset = offset
        tile_set = random.choice(Section.TILE_SETS)
        self.tiles, self.length = self.create_tiles(tile_set, space)
        #self.check_point = check_point
        self.completed = False

    def create_tiles(self, array, space):
        tiles = []
        height = len(array) - 1
        for y, row in enumerate(array):
            for x, val in enumerate(row):
                if val == 1:
                    tiles.append(Tile(x + self.offset, height - y, space))
        length = len(array[0])
        return tiles, length

    def complete(self):
        self.check_point.complete = True

class SSBGame(pyglet.window.Window):

    COLORS = [Color.RED, Color.BLUE, Color.YELLOW]

    GRAVITY = (0.0, -500.0)
    PHYSICS_FRAMERATE = 1.0 / 80

    DEATH_Y = -80

    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 480
    WINDOW_DIM = (WINDOW_WIDTH, WINDOW_HEIGHT)

    SCROLL_RATE = 6
    SCROLL_DELAY = 2

    START_PROJECTION = (-Tile.SIZE, WINDOW_HEIGHT - Tile.SIZE , WINDOW_WIDTH - Tile.SIZE, -Tile.SIZE)
    PROJECTION_SCROLL = (SCROLL_RATE, 0, SCROLL_RATE, 0)

    SCORE_FONT = 'monospace'
    SCORE_SIZE = 36
    SCORE_OFFSET = 50
    SCORE_SPACING = (WINDOW_WIDTH / 3)
    SCORE_Y = WINDOW_HEIGHT - 100


    def __init__(self, *args, **kwargs):
        super(SSBGame, self).__init__(*args, **kwargs)
        
        # Window settings
        self.width, self.height = SSBGame.WINDOW_DIM

        # rabbyt set up
        rabbyt.set_default_attribs()

        self.start()

    def start(self):

        # Create players
        self.players = []
        self.score_labels = []
        for i, color in enumerate(SSBGame.COLORS):
            player = Player(color=color)
            self.players.append(player)
            # Score Labels
            label = pyglet.text.Label('0', 
                        #font_name = SSBGame.SCORE_FONT, 
                        font_size = SSBGame.SCORE_SIZE,
                        bold = True,
                        color = color.tup(),
                        x = i * SSBGame.SCORE_SPACING + SSBGame.SCORE_OFFSET,
                        y = SSBGame.SCORE_Y)
            self.score_labels.append(label)


        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = SSBGame.GRAVITY

        # Create entities
        self.entities = []
        self.bros = []
        for i, player in enumerate(self.players):
            self.add_bro(player, y=(i+2)*50)

        # Create first section
        self.sections = deque()
        self.current_distance = 0
        self.push_section()

        # track fps
        self.fps_display = pyglet.clock.ClockDisplay()

        # slowly panning camera
        self.camera = SSBGame.START_PROJECTION

        # Game state
        self.scroll_delay = SSBGame.SCROLL_DELAY

        # Schedule updating game
        pyglet.clock.schedule(rabbyt.add_time)
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update_physics, SSBGame.PHYSICS_FRAMERATE)

    def update(self, dt):

        # Scroll viewport or decrement scroll delay
        if self.scroll_delay > 0:
            self.scroll_delay -= dt
            dscroll = max(0, dt - self.scroll_delay)
        else:
            dscroll = dt
        dcamera = SSBGame.get_scroll(dscroll) 
        self.camera = addt(self.camera, dcamera)

        # update entities
        for entity in self.entities:
            entity.update(dt)

        # Kill bros that have fallen
        for player in self.players:
            bro = player.active_bro()
            if bro.y <= SSBGame.DEATH_Y:
                self.kill_bro(bro)
                self.add_bro(player)

        # Drop tiles

        # update score labels
        for player, label in zip(self.players, self.score_labels):
            label.text = str(player.distance)

    def update_physics(self, dt):
        self.space.step(dt)

    @staticmethod
    def get_scroll(dt):
        return (map(lambda x: x * dt, SSBGame.PROJECTION_SCROLL))

    def on_draw(self):
        rabbyt.clear()

        # Draw transformed sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=self.camera)
        rabbyt.render_unsorted(self.entities)

        # Draw static sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=SSBGame.START_PROJECTION)
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
            self.start()

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
        bro = Bro(player, self.space, y=y)
        self.entities.append(bro)
        self.bros.append(bro)

    def kill_bro(self, bro):
        bro.die()
        self.entities.remove(bro)
        self.bros.remove(bro)

    def push_section(self):
        section = Section(self.current_distance, self.space)
        self.sections.append(section)
        self.entities += section.tiles
        self.current_distance += section.length

    def pop_section(self):
        section = self.sections.popleft()
        for tile in section.tiles:
            self.entities.remove(tile)
            self.space.remove(tile.pymunk_shape)

# Start game when running this file 
if __name__ == '__main__':
    game = SSBGame()
    pyglet.app.run()
