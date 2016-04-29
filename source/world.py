import sdl2
from misc import Rectangle
from audio import AudioManager

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CAMERA_SPEED = 300


class World(object):
    """Represent the world in wich the player moves.
    It contains the list of all the ennemies on-screen or not,
    the bullets shot by ennemies,
    the lasers shot by the player,
    and other things like score, remaining lives, etc.
    """

    def __init__(self):
        self.active_ennemies = []
        self.standby_ennemies = []
        self.theme = None
        self.camera = Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bulletextend = Rectangle(-200, -200, SCREEN_WIDTH + 400, SCREEN_HEIGHT + 400)
        self.playership = None
        self.score = 0
        self.score_multiplier = 1
        self.cameraspeed = 300
        self.bullets = []
        self.powerups = []
        self.gameover = False
        self.life = 1

    def update(self, delta):
        """Update everything within the world. Check for ennemies appearance,
        bullet collision, etc.
        """
        if not self.playership:
            raise Exception("Player ship not initialized. Use set world.playership.")
        # Standby ennemies check.
        for en in self.standby_ennemies:
            if en.activate():
                self.standby_ennemies.remove(en)
                self.active_ennemies.append(en)
            else:
                # self.standby_ennemies should be a queue sorted with
                break
        # Active ennemies udpate
        for en in self.active_ennemies:
            en.update(delta)
            if en.destroyed:
                self.score += en.scorevalue * self.score_multiplier
                en.destroy()
                self.active_ennemies.remove(en)
            if en.desactivate():
                self.active_ennemies.remove(en)
        # bullets update
        for bullet in self.bullets:
            if bullet.update(delta, self):
                self.bullets.remove(bullet)
        for p in self.powerups:
            if p.update(self, delta):
                self.powerups.remove(p)
        # player ship update
        self.playership.update(delta)
        # camera update
        self.camera.y -= self.cameraspeed * delta
        self.bulletextend.y -= self.cameraspeed * delta
        self.playership.hitbox.y -= self.cameraspeed * delta

    def draw(self, graphics):
        """Draw the world on the screen."""
        for en in self.active_ennemies:
            en.draw(graphics)
        for bullet in self.bullets:
            bullet.draw(graphics, self.camera)
        for p in self.powerups:
            p.draw(graphics, self.camera)
        self.playership.draw(graphics)
        pass

    def player_hit(self):
        """Method called when the player is hit by an ennemy ship or bullet.
        Make a recovery time for the ship after collision"""
        if not(self.playership.recover):
            AudioManager.play_sound("explosion")
            self.life -= 1
            self.playership.recover = True
            self.score_multiplier = 1
