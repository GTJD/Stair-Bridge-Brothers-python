import pyglet
import pymunk
import rabbyt

from collections import deque

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

    def active_bro(self):
        if len(self.bros) > 0:
            return self.bros[-1]
        else:
            return None

# An avatar controlled by a Player
class Bro(rabbyt.Sprite):

    MASS = 10
    FRICTION = 0.5
    SIZE = 32 

    JUMP_VECTOR = (0, 2000)
    SPEED = 100

    FROZEN_OPACITY = 0.8

    def __init__(self, player, space, *args, **kwargs):
        self.player = player
        self.color = player.color
        self.dead = False
        self.frozen = False
        self.space = space
        super(Bro, self).__init__(texture=resources.red)
        self.player.bros.append(self)

        self.red = 0.5
        self.green = 0.5
        self.blue = 0.5

        # Physics setup
        x = 0
        y = 100
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

        if self.moving_left:
            target_velocity = -Bro.SPEED
        elif self.moving_right:
            target_velocity = Bro.SPEED
        else:
            target_velocity = 0

        self.pymunk_body.velocity.x = target_velocity

    def freeze(self):
        self.frozen = True
        self.player.freezes += 1

        # make sprite transparent
        self.alpha = Bro.FROZEN_OPACITY

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
        self.space.remove(self.pymunk_body)

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
    RED = 0
    BLUE = 1
    YELLOW = 2

# A single tile making up the world
class Tile(rabbyt.Sprite):

    FRICTION = 0.5
    SIZE = 32

    def __init__(self, x, y, space, *args, **kwargs):
        self.space = space
        super(Tile, self).__init__(texture=resources.red)

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

    DEFAULT = [
            [0,0,0,1,0,0,0],
            [0,0,1,1,1,1,0],
            [1,1,1,1,1,1,1],
            ]

    def __init__(self, offset, space, *args, **kwargs):
        self.offset = offset
        self.tiles, self.length = self.create_tiles(Section.DEFAULT, space)
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

    WINDOW_DIM = (640, 480)
    START_PROJECTION = (-Tile.SIZE, WINDOW_DIM[1] -Tile.SIZE , WINDOW_DIM[0] - Tile.SIZE, -Tile.SIZE)
    SCROLL_RATE = 0.1
    PROJECTION_SCROLL = (SCROLL_RATE, 0, SCROLL_RATE, 0)

    def __init__(self, *args, **kwargs):
        super(SSBGame, self).__init__(*args, **kwargs)
        
        # Window settings
        self.width, self.height = SSBGame.WINDOW_DIM

        # rabbyt set up
        rabbyt.set_default_attribs()

        # Create players
        self.players = []
        for color in SSBGame.COLORS:
            self.players.append(Player(color=color))

        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = SSBGame.GRAVITY

        # Create entities
        self.entities = []
        self.bros = []
        #for player in self.players:
            #self.add_bro(player)
        self.add_bro(self.players[0])

        # Create first section
        self.sections = deque()
        self.current_distance = 0
        self.push_section()

        # Schedule updating game
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule(rabbyt.add_time)

        # track fps
        self.fps_display = pyglet.clock.ClockDisplay()

        # slowly panning camera
        self.camera = SSBGame.START_PROJECTION

    def update(self, dt):
        # Scroll viewport
        self.camera = addt(self.camera, SSBGame.PROJECTION_SCROLL)
        # update entities
        for entity in self.entities:
            entity.update(dt)
        # update physics
        self.space.step(dt)

    def on_draw(self):
        rabbyt.clear()
        # Draw transformed sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=self.camera)
        rabbyt.render_unsorted(self.entities)
        #for entity in self.entities:
            #if entity.shape:
                #entity.render()
        # Draw static sprites
        rabbyt.set_viewport(SSBGame.WINDOW_DIM, projection=(0, SSBGame.WINDOW_DIM[1], SSBGame.WINDOW_DIM[0], 0))
        self.fps_display.draw()

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

    def add_bro(self, player):
        bro = Bro(player, self.space)
        self.entities.append(bro)
        self.bros.append(bro)

    def remove_bro(self, bro):
        self.entities.remove(bro)
        self.bros.remove(bro)
        self.space.remove(bro.pymunk_body, bro.pymunk_shape)

    def push_section(self):
        section = Section(self.current_distance, self.space)
        self.sections.append(section)
        self.entities += section.tiles
        self.current_distance += section.length

    def pop_section(self):
        section = self.sections.popleft()
        for tile in section.tiles:
            self.entities.remove(tile)

# Start game when running this file 
if __name__ == '__main__':
    game = SSBGame()
    pyglet.app.run()
