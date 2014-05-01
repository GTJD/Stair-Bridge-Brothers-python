import entity
import resources

# An avatar controlled by a Player
class Bro(entity.Entity):

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

