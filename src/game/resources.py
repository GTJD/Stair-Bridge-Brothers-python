import pyglet

pyglet.resource.path = ['../res']
pyglet.resource.reindex()

box = pyglet.resource.image("box.png")
checkpoint = pyglet.resource.image("checkpoint.png")
background = pyglet.resource.image("background.png")
