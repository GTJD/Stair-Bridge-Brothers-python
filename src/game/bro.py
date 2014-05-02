import entity
import tile
import resources

import weakref

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
        if val is None:
            self._last_tile = None
        else:
            self._last_tile = weakref.ref(val)

    def __init__(self, player, space, x=0, y=0, last_tile=None, *args, **kwargs):
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
        self.last_tile = last_tile
        self.player.bros.append(self)
        self.in_air = True

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

        # set collision type for physics callbacks
        self.pymunk_shape.collision_type = Bro.FROZEN_COLLISION_TYPE

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
        # remove body from physics space
        self.space.remove(self.pymunk_body, self.pymunk_shape)

    def alive(self):
        return not self.dead and not self.frozen

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

    @staticmethod
    def setup_collision_handlers(space):
        space.collision_bias = 0
        # custom collsion handlers
        space.add_collision_handler(
                Bro.COLLISION_TYPE, 
                tile.Tile.COLLISION_TYPE,
                #begin = Bro.register_last_tile_collision_handler,
                pre_solve = Bro.seperate_from_tile_collision_handler,
                separate = Bro.prevent_jump_collision_handler
                )

    @staticmethod
    def seperate_from_tile_collision_handler(space, arbiter):
        bro_shape = arbiter.shapes[0]
        body = bro_shape.body
        contact = arbiter.contacts[0]
        contact.normal.x = round(contact.normal.x, 1)
        contact.normal.y = round(contact.normal.y, 1)
        if contact.normal.x != 0:
            body.velocity.x = -contact.normal.x

        bro = bro_shape.entity
        handle = True
        return handle

    @staticmethod
    def allow_jump_collision_handler(space, arbiter):
        pass

    @staticmethod
    def prevent_jump_collision_handler(space, arbiter):
        return True

    @staticmethod
    def register_last_tile_collision_handler(space, arbiter):
        # Only record the tile if we are landing on top of it
        print(arbiter.contacts)
        normal = arbiter.contacts[0].normal
        # This doesn't take rotation into account
        contact.distance = round(contact.distance, 1)
        if normal.y < 0 :
            bro_shape = arbiter.shapes[0]
            tile_shape = arbiter.shapes[0]
            bro = bro_shape.entity
            tile = tile_shape.entity
            bro.last_tile = tile
        return True
