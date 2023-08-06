import pygame

class Window:

    def __init__(self, dimensions, caption='UnnamedEnvironment', background_color = [255, 255, 255]):
        pygame.init()
        pygame.display.init()

        self.dimensions = dimensions
        self.background_color = background_color
        self.captions = caption
        self.window = pygame.display.set_mode(dimensions)
        pygame.display.set_caption(caption)

    def set_icon(self, icon_image):
        pygame.display.set_icon(icon_image.surface)

    def add_gameobject(self, gameobject):
        self.window.blit(gameobject.get_sprite(), gameobject.transform.pos)

    def set_background_color(self, color):
        self.background_color = color

    def window_functionality(self):
        self.window.fill(self.background_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate_app()

    def terminate_app(self):
        pygame.quit()
        quit()

class Transform2D:

    def __init__(self, pos=[0, 0], rot=0, scale=[1, 1]):
        self.pos = pos
        self.rot = rot
        self.scale = scale

class App:
    frames = []

    def __init__(self, window, FPS=60):
        self.window = window
        self.running = False
        self.FPS = FPS
        self.Clock = pygame.time.Clock()
        self.layers = []

    def run(self):
        self.running = True
        self.game_loop()

    def freezeframe(self):
        frame = pygame.surfarray.array3d(self.window.window)
        return frame

    def set_FPS(self, FPS):
        self.FPS = FPS

    def get_events(self):
        return pygame.event.get()

    def add_layer(self, layer):
        self.layers.append(layer)

    def game_loop(self):
        while self.running:
            self.window.window_functionality()

            for layer in self.layers:
                for gameobject in layer.components:
                    gameobject.object_update()
                    self.window.add_gameobject(gameobject)

            pygame.display.update()
            self.Clock.tick(self.FPS)

class Layer:

    def __init__(self):
        self.components = []

    def add_gameobject(self, gm):
        self.components.append(gm)

class GameObject:

    def __init__(self, sprite):
        self.sprite = sprite
        self.transform = Transform2D()

    def object_update(self):
        pass

    def set_pos(self, pos):
        self.transform.pos = pos

    def set_rot(self, rot):
        self.transform.rot = rot

    def set_scale(self, scale):
        self.transform.scale = scale

    def get_sprite(self):
        sprite = pygame.transform.rotate(self.sprite.surface, self.transform.rot)
        sprite = pygame.transform.scale(sprite, [int(self.sprite.surface.get_width() * self.transform.scale[0]),
                                                 int(self.sprite.surface.get_height() * self.transform.scale[1])])
        return sprite

class Sprite:
    def __init__(self, source):
        self.surface = pygame.image.load(source)


class ImageContentLoader:

    def __init__(self, content_dictionary):
        self.keys = list(content_dictionary.keys())
        self.content_dict = content_dictionary
        self.load_content()

    def load_content(self):
        for key in self.keys:
            self.content_dict[key] = Sprite(self.content_dict[key])

    def get_content(self):
        return self.content_dict
