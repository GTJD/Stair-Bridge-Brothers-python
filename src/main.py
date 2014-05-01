import pyglet
import pymunk
import rabbyt

from OpenGL.GL import *

import random

from collections import deque
from operator import attrgetter
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

    @property
    def static(self):
        return self._static

    @static.setter
    def static(self, val):
        # Check if value is changes
        if self.static != val:
            self._static = val
            if self.static:
                self._set_static()
                # remove body from physics space and make it static
                self.space.remove(self.pymunk_body)
            else:
                self._set_dynamic()
                # add body to physics space and make dynamic
                self.space.add(self.pymunk_body)

    def _set_static(self):
        self.pymunk_body.velocity = 0, 0
        self.pymunk_body.angular_velocity = 0
        self.pymunk_body.mass = pymunk.inf
        self.pymunk_body.moment = pymunk.inf

    def _set_dynamic(self):
        self.pymunk_body.mass = self._mass
        self.pymunk_body.moment = self._moment

    def __init__(self, 
            space, 
            friction = pymunk.inf,
            mass = pymunk.inf,
            width = 0,
            height = 0,
            x = 0,
            y = 0,
            angle = 0,
            static = False, 
            *args, **kwargs):

        super(Entity, self).__init__(*args, **kwargs)

        # Physics setup
        self.space = space
        self._mass = mass
        self._moment = pymunk.moment_for_box(mass, width, height)

        # body
        body = pymunk.Body(self._mass, self._moment)
        body.position = x, y
        body.angle = angle

        # shape
        hw = width // 2
        hh = height // 2
        vs = [(-hw, hh), (hw, hh), (hw, -hh), (-hw, -hh)]
        shape = pymunk.Poly(body, vs)
        shape.friction = friction
        space.add(shape)

        self.pymunk_shape = shape
        self.pymunk_body = body
        if static: self._set_static()

        # force static state update if not static
        self._static = True
        self.static = static

    def update(self, dt):
        self.x = self.pymunk_body.position.x
        self.y = self.pymunk_body.position.y
        self.rot = degrees(self.pymunk_body.angle)

    def remove_from_space(self):
        self.space.remove(self.pymunk_shape)
        if not self.static:
            self.space.remove(self.pymunk_body)

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
        super(Bro, self).__init__(space, 
                x = x,
                y = y,
                mass = Bro.MASS,
                friction = Bro.FRICTION,
                width = Bro.SIZE,
                height = Bro.SIZE,
                texture = resources.box)
        self.player = player
        self.color = player.color
        self.dead = False
        self.frozen = False
        self.player.bros.append(self)

        # Model state
        self.jumping = False
        self.moving_left = False
        self.moving_right = False

    def update(self, dt):
        super(Bro, self).update(dt)

        # Move based on input
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
        self.static = True
        self.player.freezes += 1

        self.stop()

        # Fade sprite
        self.red += Bro.FREEZE_FADE
        self.green += Bro.FREEZE_FADE 
        self.blue += Bro.FREEZE_FADE

    def drop(self):
        if self.frozen:
            self.static = False

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

    def stop(self):
        self.stop_right()
        self.stop_left()

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

    MASS = 20
    FRICTION = 0.5
    SIZE = 32

    WHITE_RATIO = 0.5

    BRIGHTNESS_MIN = 0.7
    BRIGHTNESS_RANGE = 1.0 - BRIGHTNESS_MIN

    DROP_IMPULSES = [ (100, 0), (-100,0) ]

    DROP_OFFSET = (0, SIZE // 2)

    def __init__(self, x, y, space, *args, **kwargs):
        self.space = space
        super(Tile, self).__init__(space,
                x = x * Tile.SIZE,
                y = y * Tile.SIZE,
                angle = 0,
                width = Tile.SIZE,
                height = Tile.SIZE,
                friction = Tile.FRICTION,
                mass = Tile.MASS,
                static = True,
                texture=resources.box)

        # random colour
        if random.random() < Tile.WHITE_RATIO:
            brightness = random.random() % Tile.BRIGHTNESS_RANGE + Tile.BRIGHTNESS_MIN
            self.red = brightness
            self.green = brightness
            self.blue = brightness

    def drop(self):
        self.static = False
        self.pymunk_body.apply_impulse(random.choice(Tile.DROP_IMPULSES), Tile.DROP_OFFSET)

# A goal that players reach at the end of a Section
class CheckPoint(Entity):

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
        ],
        [
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [1,1,1,1,1,1,0,1,1],
        ],
        [
            [0,0,0,0,0,1,1,1,0],
            [0,0,0,0,0,1,1,1,0],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,1,1,1,1],
            [0,0,0,0,0,0,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,1,1],
            [0,0,0,0,0,1,0,0,0],
            [1,1,1,1,1,1,0,1,1],
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

    def first_tile_offset(self):
        min_tile = min(self.tiles, key = attrgetter('x'))
        return min_tile.x

class SSBGame(pyglet.window.Window):

    BACKGROUND = pyglet.image.TileableTexture.create_for_image(resources.background)

    COLORS = [Color.RED, Color.BLUE, Color.YELLOW]

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
        self.camera = SSBGame.START_PROJECTION

        # Game state
        self.scroll_delay = SSBGame.SCROLL_DELAY
        self.drop_line = SSBGame.DROP_LINE_START

        # Schedule updating game
        pyglet.clock.schedule(rabbyt.add_time)
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update_physics, SSBGame.PHYSICS_FRAMERATE)

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

        dcamera = SSBGame.get_scroll(dscroll) 
        self.camera = addt(self.camera, dcamera)

        self.drop_line += dscroll * SSBGame.SCROLL_RATE

        # update entities
        for entity in self.entities:
            entity.update(dt)

        # Kill bros that have fallen
        for bro in self.bros:
            if bro.y < SSBGame.DEATH_Y:
                self.kill_bro(bro)
            elif bro.x < self.drop_line:
                bro.drop()

        for tile in self.sections[0].tiles:
            # Remove fallen tiles
            if tile.y < SSBGame.DEATH_Y:
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
        while self.current_distance * Tile.SIZE < self.populate_distance():
            self.push_section()

    def update_physics(self, dt):
        self.space.step(dt)

    def camera_distance(self):
        return self.camera[2]

    def populate_distance(self):
        return self.camera_distance() + SSBGame.POPULATE_PADDING

    @staticmethod
    def get_scroll(dt):
        return (map(lambda x: x * dt, SSBGame.PROJECTION_SCROLL))

    def on_draw(self):
        rabbyt.clear()

        # Draw background
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=SSBGame.STATIC_PROJECTION)
        # reset opengl draw colour
        glColor(255, 255, 255, 1)
        SSBGame.BACKGROUND.blit_tiled(0, 0, 0, self.width, self.height)

        # Draw transformed sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=self.camera)
        rabbyt.render_unsorted(self.entities)

        # Draw static sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=SSBGame.STATIC_PROJECTION)
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
        bro = Bro(player, self.space, x=x, y=y)
        self.entities.append(bro)
        self.bros.append(bro)

    def kill_bro(self, bro):
        bro.die()
        self.entities.remove(bro)
        self.bros.remove(bro)
        if not bro.frozen:
            self.add_bro(bro.player)

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

    def remove_section(self, section):
        self.sections.remove(section)

# Start game when running this file 
if __name__ == '__main__':
    game = SSBGame()
    pyglet.app.run()
