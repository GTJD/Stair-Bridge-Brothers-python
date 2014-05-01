import rabbyt
import pymunk
from math import degrees

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
