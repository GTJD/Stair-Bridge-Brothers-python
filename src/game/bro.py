import entity
import tile
import resources

import weakref
from pyglet.app import WeakSet

# An avatar controlled by a Player
class Bro(entity.Entity):

    MASS = 10
    FRICTION = 0
    SIZE = 32 

    JUMP_VECTOR = (0, 2000)
    SPEED = 100

    FREEZE_FADE = 0.3

    COLLISION_TYPE = 2
    FROZEN_COLLISION_TYPE = 3

    @property
    def color(self):
        return self._color 

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

    @property
    def last_tile(self):
        if self._last_tile is None:
            return None
        else:
            return self._last_tile()

    @last_tile.setter
    def last_tile(self, val):
        # untint old last tile
        if self._last_tile is not None:
            self._last_tile().unset_last_tile_for(self)

        if val is None:
            self._last_tile = None
        else:
            self._last_tile = weakref.ref(val)
            self._last_tile().set_last_tile_for(self)

    def __init__(self, player, space, x=0, y=0, old_bro=None, *args, **kwargs):
        super(Bro, self).__init__(space, 
                x = x,
                y = y,
                mass = Bro.MASS,
                friction = Bro.FRICTION,
                collision_type = Bro.COLLISION_TYPE,
                width = Bro.SIZE,
                height = Bro.SIZE,
                texture = resources.box)
        self.player = player
        self.color = player.color
        self.dead = False
        self.frozen = False
        self.player.bros.append(self)

        # Model state
        self.moving_left = False
        self.moving_right = False
        self.collide_left = False
        self.collide_right = False
        self.shapes_below = WeakSet()
        self._last_tile = None

        # get old bro values
        if old_bro is not None:
            self.moving_left = old_bro.moving_left
            self.moving_right = old_bro.moving_right
            self.last_tile = old_bro.last_tile

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

        # set collision type for physics callbacks
        #self.pymunk_shape.collision_type = Bro.FROZEN_COLLISION_TYPE

        # Fade sprite
        self.red += Bro.FREEZE_FADE
        self.green += Bro.FREEZE_FADE 
        self.blue += Bro.FREEZE_FADE

    def drop(self):
        if self.frozen:
            self.static = False

    def die(self):
        self.dead = True
        if not self.frozen:
            self.player.deaths += 1
        # unset last tile
        self.last_tile = None
        # remove body from physics space
        self.space.remove(self.pymunk_body, self.pymunk_shape)

    def alive(self):
        return not self.dead and not self.frozen

    def jump(self):
        if self.can_jump():
            self.pymunk_body.apply_impulse(Bro.JUMP_VECTOR, (0, 0))

    def can_jump(self):
        return len(self.shapes_below) > 0

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

    @staticmethod
    def setup_collision_handlers(outer_space):

        # Prior to solbing collision
        def pre_solve_handler(space, arbiter):
            contact = arbiter.contacts[0]

            a = arbiter.shapes[0]
            b = arbiter.shapes[1]
            # if a is above b
            if a.body.position.y - b.body.position.y > 0:
                record_shape_below(a, b)
            # otherwise b is above a
            else:
                record_shape_below(b, a)

            # Allow sliding down walls (sorta, we still catch on 'corners')
            if round(contact.normal.x) == 1:
                body = arbiter.shapes[0].body
                bro = body.entity
                #body.velocity.x = contact.normal.x * Bro.SPEED

            return True

        def record_shape_below(above, below):
            bro = above.entity
            if type(bro) is Bro and not bro.frozen:
                # record this as an object under us
                bro.shapes_below.add(below)

                # check if we should record the last tile for this bro
                t = below.entity
                if type(t) is tile.Tile:
                    bro.last_tile = t

        # When first seperating
        def separate_handler(space, arbiter):
            # One less object below
            bro_shape = arbiter.shapes[0]
            bro = bro_shape.entity
            other_shape = arbiter.shapes[1]
            other = other_shape.entity

            # Remove object if it was below 
            if other_shape in bro.shapes_below:
                bro.shapes_below.remove(other_shape)

            return True

        def shape_below(arbiter):
            bro_shape = arbiter.shapes[0]
            tile_shape = arbiter.shapes[1]
            bro_body = bro_shape.body
            tile_body = tile_shape.body
            return bro_body.position.y > tile_body.position.y

        # Handlers between bros and tiles
        outer_space.add_collision_handler(
                Bro.COLLISION_TYPE, 
                tile.Tile.COLLISION_TYPE,
                pre_solve = pre_solve_handler,
                separate = separate_handler
            )

        # Handlers between bros
        outer_space.add_collision_handler(
                Bro.COLLISION_TYPE, 
                Bro.COLLISION_TYPE, 
                pre_solve = pre_solve_handler,
                separate = separate_handler
            )
