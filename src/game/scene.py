import pyglet
import pymunk
import rabbyt

import color
import resources
from player import Player
from tile import Tile
from bro import Bro
from section import Section

from OpenGL.GL import *
from collections import deque

class Scene(object):
    def __init__(self, game, *args, **kwargs):
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

    def on_draw(self):
        pass

    def on_key_pressed(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_resize(self, width, height):
        pass

class GameScene(Scene):

    BACKGROUND = pyglet.image.TileableTexture.create_for_image(resources.background)

    COLORS = (color.RED, color.BLUE, color.YELLOW)

    GRAVITY = (0.0, -500.0)
    PHYSICS_FRAMERATE = 1.0 / 80

    DEATH_Y = -80

    SCROLL_RATE = 10
    SCROLL_ACCL = 0.4
    SCROLL_DELAY = 2
    DROP_LINE_START = -150

    START_PROJECTION_X = -200
    START_PROJECTION_Y = -32

    # Logical game size
    GAME_WIDTH = 900
    GAME_HEIGHT = 480

    SCORE_ALIVE_ALPHA =  255
    SCORE_DEAD_ALPHA = int(0.5 * 255)
    SCORE_SIZE = 36
    SCORE_OFFSET = 50
    SCORE_SPACING = 1.0 / 3
    SCORE_Y_OFFSET = 100

    POPULATE_PADDING = 50

    KEY_BINDINGS = {
            0: {
                'left': pyglet.window.key.LEFT,
                'right': pyglet.window.key.RIGHT,
                'jump': pyglet.window.key.UP,
                'freeze': pyglet.window.key.DOWN
                },
            1: {
                'left': pyglet.window.key.A,
                'right': pyglet.window.key.D,
                'jump': pyglet.window.key.W,
                'freeze': pyglet.window.key.S
                },
            2: {
                'left': pyglet.window.key.J,
                'right': pyglet.window.key.L,
                'jump': pyglet.window.key.I,
                'freeze': pyglet.window.key.K
                }
            }

    def __init__(self, game, *args, **kwargs):
        super(GameScene, self).__init__(game, *args, **kwargs)

    def start(self):
        # Create players
        self.players = []
        self.score_labels = []
        for i, color in enumerate(GameScene.COLORS):
            player = Player(color)
            self.players.append(player)
            # player input handlers
            keys = GameScene.KEY_BINDINGS[i]
            player.input_handler = self.create_input_handler(player, 
                    jump = keys['jump'],
                    left = keys['left'],
                    right = keys['right'],
                    freeze = keys['freeze'])
            # Score Labels
            label_color = color.tup() + (GameScene.SCORE_ALIVE_ALPHA,)
            label = pyglet.text.Label('0', 
                        font_size = GameScene.SCORE_SIZE,
                        bold = True,
                        color = label_color)
            self.score_labels.append(label)
            player.score_label = label
        self.position_labels()

        # Create physics space
        self.space = pymunk.Space()
        # Instantly correct collisions
        #self.space.collision_bias = 0
        self.space.gravity = GameScene.GRAVITY
        Bro.setup_collision_handlers(self.space)

        # Create first section
        self.entities = []
        self.sections = deque()
        self.current_distance = 0
        self.push_section()

        # Create entities
        self.bros = []
        for i, player in enumerate(self.players):
            self.add_bro(player, y=(i+2)*50)

        # slowly panning camera
        self.camera = self.start_projection()

        # Game state
        self.scroll_delay = GameScene.SCROLL_DELAY
        self.scroll_rate =  GameScene.SCROLL_RATE
        self.drop_line = GameScene.DROP_LINE_START

        # Schedule updating game
        pyglet.clock.schedule(rabbyt.add_time)
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update_physics, GameScene.PHYSICS_FRAMERATE)

    def start_projection(self):
        left = GameScene.START_PROJECTION_X
        bottom = GameScene.START_PROJECTION_Y
        width = GameScene.GAME_WIDTH    
        height = GameScene.GAME_HEIGHT
        right = width + left
        top = height + bottom
        #print(float(width) / height)
        return (left, top, right, bottom)
    
    def draw_area(self):
        window_ratio = float(self.game.width) / self.game.height
        game_ratio = float(GameScene.GAME_WIDTH) / GameScene.GAME_HEIGHT
        #print("g: %s, w: %s" % (game_ratio, window_ratio))
        # limited by height
        if window_ratio > game_ratio:
            width = self.game.height * game_ratio
            height = self.game.height
        # limited by width
        else:
            width = self.game.width
            height = self.game.width / game_ratio
        left = int((self.game.width - width) / 2)
        bottom = int((self.game.height - height) / 2)
        top = int(bottom + height)
        right = int(left + width)
        #print(self.game.get_size())
        #print(left, bottom, width, height)
        #print (left, top, right, bottom)
        #return (left, top, right, bottom)
        return (width, height)

    def position_labels(self):
        for i, label in enumerate(self.score_labels):
            label.x = i * GameScene.SCORE_SPACING * self.game.width + GameScene.SCORE_OFFSET
            label.y = self.game.height - GameScene.SCORE_Y_OFFSET

    def stop(self):
        pyglet.clock.unschedule(rabbyt.add_time)
        pyglet.clock.unschedule(self.update)
        pyglet.clock.unschedule(self.update_physics)

    def end(self):
        print("The game is over we should move to a final score screen")
        self.reset()

    def update(self, dt):

        # Scroll the game and camera
        self.scroll(dt)

        # update entities
        for entity in self.entities:
            entity.update(dt)

        # Kill bros that have fallen
        for bro in self.bros:
            if bro.y < GameScene.DEATH_Y:
                self.kill_bro(bro)
            elif bro.x < self.drop_line:
                bro.drop()

        for tile in self.sections[0].tiles:
            # Remove fallen tiles
            if tile.y < GameScene.DEATH_Y:
                self.sections[0].tiles.remove(tile)
                self.entities.remove(tile)
            # Drop tiles behind drop line
            elif tile.x < self.drop_line:
                pass
                #tile.drop()

        # delete empty sections
        if len(self.sections[0].active_tiles()) == 0:
            self.pop_section()

        # update score labels
        for player, label in zip(self.players, self.score_labels):
            label.text = str(player.distance)

        # add sections 
        while self.current_distance * Tile.SIZE < self.populate_distance():
            self.push_section()

    def scroll(self, dt):
        # Scroll viewport or decrement scroll delay
        if self.scroll_delay > 0:
            self.scroll_delay -= dt
            dscroll = max(0, dt - self.scroll_delay)
        else:
            dscroll = dt

        # Accelerate scrolling
        self.scroll_rate += GameScene.SCROLL_ACCL * dscroll

        # move camera projection
        dcamera = GameScene.get_scroll(dscroll, self.scroll_rate) 
        self.camera = GameScene.addt(self.camera, dcamera)

        # move line that drops entities
        self.drop_line += dscroll * self.scroll_rate

    # Add tuple element-wise
    @staticmethod
    def addt(a, b):
        return (map(sum,zip(a,b)))

    @staticmethod
    def get_scroll(dt, rate):
        return (map(lambda x: x * rate * dt, (1, 0, 1, 0)))

    def update_physics(self, dt):
        self.space.step(dt)

    def camera_distance(self):
        return self.camera[2]

    def populate_distance(self):
        return self.camera_distance() + GameScene.POPULATE_PADDING

    def create_input_handler(self, player, left, right, jump, freeze):
        def input_handler(pressed, symbol, modifiers):
            # See if there is a bro to use the input
            bro = player.active_bro()
            if bro:
                # If the key was pressed
                if pressed:
                    if symbol == jump:
                        bro.jump()
                        return True
                    elif symbol == left:
                        bro.move_left()
                        return True
                    elif symbol == right:
                        bro.move_right()
                        return True
                    elif symbol == freeze:
                        self.freeze_bro(bro)
                        return True
                # else released key
                else:
                    if symbol == left:
                        bro.stop_left()
                        return True
                    elif symbol == right:
                        bro.stop_right()
                        return True
           # fall through if we did not handle the input
            return False

        return input_handler

    def get_bro(self, num):
        p = self.players[0]
        return p.active_bro()

    def add_bro(self, player, old_bro=None, x=0, y=100):
        #x = self.sections[0].first_tile_offset()
        if old_bro is not None:
            x = old_bro.last_tile.x
            y = old_bro.last_tile.y + Tile.SIZE
        bro = Bro(player, self.space, x=x, y=y, old_bro=old_bro)
        self.entities.append(bro)
        self.bros.append(bro)

    def kill_bro(self, bro):
        self.entities.remove(bro)
        self.bros.remove(bro)
        if bro.alive():
            bro.die()
            # Change label color
            player = bro.player
            player.score_label.color = player.color.tup() + (GameScene.SCORE_DEAD_ALPHA,)
        # Check if this was the last bro standing
        if not self.bros_remaining():
            self.end()

    def bros_remaining(self):
        for player in self.players:
            if player.active_bro() is not None:
                return True
        return False

    def freeze_bro(self, bro):
        # Prevent us from freezing if there is not last tile or the tile has dropped
        if bro.last_tile is not None and bro.last_tile.static:
            self.add_bro(bro.player, old_bro=bro)
            bro.freeze()

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


    def on_draw(self):
        draw_area = self.draw_area()
        static_projection = (0, draw_area[1], draw_area[0], 0)
        # Draw background
        rabbyt.set_viewport(draw_area, projection = static_projection)
        # reset opengl draw colour
        glColor(255, 255, 255, 1)
        GameScene.BACKGROUND.blit_tiled(0, 0, 0, draw_area[0], draw_area[1])

        # Draw transformed sprites
        rabbyt.set_viewport(draw_area, projection = self.camera)
        rabbyt.render_unsorted(self.entities)

        # Draw static sprites
        rabbyt.set_viewport(draw_area, projection = static_projection)
        for label in self.score_labels:
            label.draw()

    def on_key_press(self, symbol, modifiers):
        for player in self.players:
            if player.input_handler(True, symbol, modifiers): break

    def on_key_release(self, symbol, modifiers):
        for player in self.players:
            if player.input_handler(False, symbol, modifiers): break

    def on_resize(self, width, height):
        self.position_labels()

class StartScene(Scene):
    pass

class EndScene(Scene):
    pass
