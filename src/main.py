import pyglet
import rabbyt

## Classes ##

# An object that can be started and stopped
class ActiveObject(object):

    def __init__(self, *args, **kwargs):
        self.active = active
        self.window = window 

    def stop(self):
        self.active = False

    def start(self):
        self.active = True

    def toggle_active(self):
        self.active = not self.active

# The top level object containting Players, Scenes, and various controllers
class Game(ActiveObject):

    def __init__(self, *args, **kwargs):
        super(ActiveObject, self).__init__(*args, **kwargs)
        self.players = []
        self.scenes = []
        self.views = []

    def update(self, dt):
        if self.active:
            for scene in self.scenes:
                scene.update(dt)

    def on_draw(self):
        for view in self.views:
            view.on_draw()

# Used to display the contents of a Game
class View(object):

    def __init__(self, *args, **kwargs):
        super(ActiveObject, self).__init__(*args, **kwargs)

# A view the draws a scene to a window
class WindowView(pyglet.window.Window, View):

    def __init__(self, scene, *args, **kwargs):
        super(WindowView, self).__init__(*args, **kwargs)
        self.scene = scene

    def on_draw(self):
        self.clear()
        for entity in self.scene.entities:
            if hasattr(entity, 'draw') and callable(getattr(entity, 'draw')):
                entity.draw()

# Represents an actual player of the game
class Player(object):

    def __init__(self, color, *args, **kwargs):
        self.score = 0
        self.bros = []
        self.color = color
        self.deaths = 0
        self.freezes = 0

# A collection of Entities
class Scene(ActiveObject):

    def __init__(self, *args, **kwargs):
        super(ActiveObject, self).__init__(*args, **kwargs)
        self.entities = []
        self.visible = False

    def update(self, dt):
        if self.active:
            for entity in self.entities:
                entity.update(dt)

# A 'physical' object that exists whith a scene
class Entity(ActiveObject, pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super(ActiveObject, self).__init__(*args, **kwargs)
        super(Entity, self).__init__(*args, **kwargs)

    def update(self, dt):
        pass


# An entity with a sprite to render
class SpriteEntity(Entity, rabbyt.sprites.Sprite):

    def draw(self):
        self.render()

# An avatar controlled by a Player
class Bro(Entity):

    def __init__(self, player, color, *args, **kwargs):
        self.frozen = False
        self.player = player
        self.color = color
        self.dead = False

    def update(self, dt):
        pass

    def freeze(self):
        self.frozen = True
        self.player.freezes += 1

    def die(self):
        self.dead = True
        self.player.deaths += 1

# A Bro's color
class Color(object):
    RED = 0
    BLUE = 1
    YELLOW = 2

# A single tile making up the world
class Tile(Entity):
    pass    

# A goal that players reach at the end of a Section
class CheckPoint(Entity):
    pass

# A collection of Tiles with a CheckPoint at the end
class Section(object):

    def __init__(self, *args, **kwargs):
        self.tiles = tiles
        self.check_point = check_point
        self.completed = False

    @staticmethod
    def random_section():
        pass

    def complete(self):
        self.complete = True

    def length(self):
        self.length = len(tiles[0])

# A series of Sections and Bros traversing them
class ActionScene(Scene):

    def __init__(self):
        super(ActionScene, self).__init__()
        self.sections = []
        self.add_section()

    def add_section(self):
        section = Section.random_section()
        self.sections.append(section)

    def remove_section(self, section):
        if section in self.sections:
            self.sections.remove(section)


class SSBGame(Game):

    COLORS = [Color.RED, Color.BLUE, Color.YELLOW]

    def __init__(self, *args, **kwargs):
        super(SSBGame, self).__init__(*args, **kwargs)
        # Create players
        for color in SSBGame.COLORS:
            self.players.append(Player(color=color))
        # Create scene
        scene = ActionScene()
        self.scenes.append(scene)
        # Create window view
        self.views.append(WindowView(scene))

# Start game when running this file 
if __name__ == '__main__':
    game = SSBGame()
    pyglet.app.run()
