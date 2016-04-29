
import sdl2
import sdl2.ext
#import sdl2.sdlgfx as gfx

import graphics


class Sprite():

    def __init__(self, graphics, filepath, sourcex, sourcey, width, height):
        self.spritesheet = graphics.load_image(filepath)
        self.sourcerect = sdl2.SDL_Rect()
        self.sourcerect.x = sourcex
        self.sourcerect.y = sourcey
        self.sourcerect.w = width
        self.sourcerect.h = height
        self.filepath = filepath

    def update(self, delta):
        pass

    def draw(self, graphics, gamex, gamey):
        destrect = sdl2.SDL_Rect()
        destrect.x = gamex
        destrect.y = gamey
        destrect.w = self.sourcerect.w
        destrect.h = self.sourcerect.h
        graphics.blit_surface(self.spritesheet, self.sourcerect, destrect)
        # graphics.blit_surface_rotated(self.spritesheet, self.sourcerect, destrect, 90)

    def draw_rotated(self, graphics, gamex, gamey, angle):
        destrect = sdl2.SDL_Rect()
        destrect.x = gamex
        destrect.y = gamey
        destrect.w = self.sourcerect.w
        destrect.h = self.sourcerect.h
        graphics.blit_surface_rotated(self.spritesheet, self.sourcerect, destrect, angle)

    def __repr__(self):
        return self.filepath + " (%d, %d, %d, %d)" % (self.sourcerect.x,
                                                      self.sourcerect.y,
                                                      self.sourcerect.w,
                                                      self.sourcerect.h)


class AnimatedSprite(Sprite):

    def __init__(self, graphics, filepath, sourcex, sourcey, width, height,
                 fps, nbframes):
        super(AnimatedSprite, self).__init__(graphics, filepath, sourcex,
                                             sourcey, width, height)
        self.frametime = 1 / fps
        self.nbframes = nbframes
        self.currentframe = 0
        self.delta = 0

    def update(self, delta):
        self.delta += delta
        if self.delta > self.frametime:
            self.currentframe += 1
            self.delta = 0
            if self.currentframe < self.nbframes:
                self.sourcerect.x += self.sourcerect.w
            else:
                self.sourcerect.x -= self.sourcerect.w * (self.nbframes - 1)
                self.currentframe = 0


class AllSprite(object):
    """Contains all the necessary sprites of the game."""
    bg = None
    player = None
    playerrecovery = None
    laser_basic = None  # default laser sprite
    bullet_small = None
    bullet_medium = None  # medium sized bullet sprite
    bullet_big = None
    en_basic = None  # basic ennemy sprite
    en_bis = None  # weird looping ennemy sprite
    en_parrot = None  # Dat parrot ennemy
    boss_cena = None  # boss sprite
    boss_carrier = None
    drone_carrier = None
    potato = None  # Menu patatoe sprite
    title = None
    pow_doom = None
    pow_mystery = None
    pow_attackspeed = None
    pow_doubleattack = None
    pow_bonus1 = None
    pow_malus2 = None
    shieldcoming = None
    shield = None
    en_rotor = None

    def __init__(self):
        raise Exception("You cant instanciate this class")

    @staticmethod
    def load_sprites(graphics):
        AllSprite.bg = Sprite(graphics, "ressources/bg_1024x1536.png", 0, 0, 1024, 1536)
        AllSprite.playerrecovery = AnimatedSprite(
            graphics, "ressources/shiprecovery_30x37.png", 0, 0, 30, 37, 8, 4)
        AllSprite.player = AnimatedSprite(
            graphics, "ressources/ship_30x37.png", 0, 0, 30, 37, 15, 2)
        AllSprite.laser_basic = Sprite(graphics, "ressources/laser_8x32.png", 0, 0, 8, 32)
        AllSprite.bullet_small = Sprite(graphics, "ressources/bullet_small_12x12.png", 0, 0, 12, 12)
        AllSprite.bullet_medium = Sprite(
            graphics, "ressources/bullet_medium_24x24.png", 0, 0, 24, 24)
        AllSprite.bullet_big = Sprite(graphics, "ressources/bullet_big_36x36.png", 0, 0, 36, 36)
        AllSprite.en_basic = AnimatedSprite(
            graphics, "ressources/ennemy1_24x40.png", 0, 0, 24, 40, 0.5, 2)
        AllSprite.en_bis = AnimatedSprite(
            graphics, "ressources/ennemy2_37x32.png", 0, 0, 37, 32, 0.25, 4)
        AllSprite.en_parrot = Sprite(graphics, "ressources/parrot_60x57.png", 0, 0, 60, 57)
        AllSprite.boss_cena = AnimatedSprite(
            graphics, "ressources/cena_289x300.png", 0, 0, 289, 300, 2, 2)
        AllSprite.boss_carrier = Sprite(graphics, "ressources/carrier_921x561.png", 0, 0, 921, 561)
        AllSprite.potato = AnimatedSprite(
            graphics, "ressources/asteroid_188x129.png", 0, 0, 188, 129, 1, 1)
        AllSprite.title = Sprite(graphics, "ressources/title.png", 0, 0, 750, 250)
        AllSprite.drone_carrier = Sprite(graphics, "ressources/drone_19x27.png", 0, 0, 19, 27)
        AllSprite.pow_doom = Sprite(graphics, "ressources/powerup/random.png", 0, 0, 32, 32)
        AllSprite.pow_mystery = Sprite(graphics, "ressources/powerup/mystery.png", 0, 0, 32, 32)
        AllSprite.pow_attackspeed = Sprite(
            graphics, "ressources/powerup/firing_speed.png", 0, 0, 32, 32)
        AllSprite.pow_doubleattack = Sprite(
            graphics, "ressources/powerup/double_laser.png", 0, 0, 32, 32)
        AllSprite.shieldcoming = AnimatedSprite(
            graphics, "ressources/shieldcoming_98x90.png", 0, 0, 98, 90, 2, 8)
        AllSprite.shield = Sprite(graphics, "ressources/shield_carrier.png", 0, 0, 98, 90)
        AllSprite.pow_bonus1 = Sprite(graphics, "ressources/powerup/multiplier1.png", 0, 0, 32, 32)
        AllSprite.pow_malus2 = Sprite(graphics, "ressources/powerup/minus2.png", 0, 0, 32, 32)
        AllSprite.pow_slow = Sprite(graphics, "ressources/powerup/slow.png", 0, 0, 32, 32)
        AllSprite.en_smallwall = Sprite(
            graphics, "ressources/small_wall_300x100.png", 0, 0, 300, 100)
        AllSprite.en_rotor = Sprite(graphics, "ressources/rotor80x60.png", 0, 0, 80, 60)
        AllSprite.en_boss3 = Sprite(graphics, "ressources/boss3_300x300.png", 0, 0, 300, 300)
