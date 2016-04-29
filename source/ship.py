import random
import math
import graphics
from sprite import AnimatedSprite, Sprite, AllSprite
from misc import Rectangle, worldToScreen, collide, cart2pol
from font import FontManager
# from music import AllAudio

from powerups import *

import sdl2

from math import sin, cos, pi, sqrt, asin, degrees

from audio import AudioManager

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


class Ship(object):
    """Abstract class representing a ship (allied or ennemy)."""

    def __init__(self, world, hitbox, sprite, spriteoffsetx=0, spriteoffsety=0):
        self.hitbox = hitbox
        self.sprite = sprite
        self.sp_offset = (spriteoffsetx, spriteoffsety)
        self.velx = 0  # px/s
        self.vely = 0  # px/s
        self.world = world

    def update(self, delta):
        """Called every frame to update the ship coordinates and other fields."""
        self.hitbox.x += self.velx * delta
        self.hitbox.y += self.vely * delta
        self.sprite.update(delta)

    def draw(self, graphics):
        """Draw the ship's sprite on the screen if it's visibl (not out of the
        window).
        """
        destx, desty = worldToScreen(
            self.hitbox.x, self.hitbox.y, self.world.camera)
        destx = int(destx + self.sp_offset[0])
        desty = int(desty + self.sp_offset[1])
        if (-self.sprite.sourcerect.w < destx < graphics.screenwidth and
                -self.sprite.sourcerect.h < desty < graphics.screenheight):
            self.sprite.draw(graphics, destx, desty)


class PlayerShip(Ship):
    """Represent the ship controlled by the player."""

    def __init__(self, world, hitbox, sprite, sp_laser, spriteoffsetx=0, spriteoffsety=0):
        super(PlayerShip, self).__init__(world, hitbox, sprite,
                                         spriteoffsetx, spriteoffsety)
        self.shotlasers = []
        # self.maxspeed = 480
        self.maxspeed = 300
        self.shootingdelay = 0.15  # seconds
        self.lastshot = self.shootingdelay
        self.sp_laser = sp_laser
        self.recover = False
        self.recoverytime = 2
        self.recoverytimer = 0
        self.initSprite = False
        self.powerup_sockets = {}
        self.time_effects = {}

        def shoot_default(self):
            """Shoot a laser."""
            if self.lastshot >= self.shootingdelay:
                x = int(self.hitbox.x + self.hitbox.w /
                        2 + random.randint(-10, 10))
                y = self.hitbox.y
                self.shotlasers.append(Laser(x, y))
                self.lastshot = 0
        self.shoot_method = shoot_default

    def update(self, delta):
        super(PlayerShip, self).update(delta)
        self.lastshot += delta
        for l in self.shotlasers:
            if l.update(self.world, delta):
                self.shotlasers.remove(l)
        self.hitbox.x = max(self.hitbox.x, self.world.camera.x)
        self.hitbox.x = min(self.hitbox.x, self.world.camera.x +
                            self.world.camera.w - self.hitbox.w)
        self.hitbox.y = max(self.hitbox.y, self.world.camera.y)
        self.hitbox.y = min(
            self.hitbox.y, self.world.camera.y +
            self.world.camera.h - self.hitbox.h)
        if self.recover:
            self.recoverytimer += delta
        if self.recoverytimer > self.recoverytime:
            self.recover = False
            self.recoverytimer = 0
            self.initSprite = True
        if self.recover:
            AllSprite.playerrecovery.update(delta)
        if self.initSprite:
            AllSprite.shieldcoming.currentframe = 0
            self.initSprite = False
        # TODO Ajouter le reste de la méthode update de PlayerShip
        to_remove = []
        for ef in self.time_effects:
            self.time_effects[ef] -= delta
            if self.time_effects[ef] <= 0:
                ef.remove(self)
                to_remove.append(ef)
        for tr in to_remove:
            self.time_effects.pop(tr)

    def shoot(self):
        self.shoot_method(self)

    def draw(self, graphics):
        destx, desty = worldToScreen(
            self.hitbox.x, self.hitbox.y, self.world.camera)
        destx = int(destx + self.sp_offset[0])
        desty = int(desty + self.sp_offset[1])
        if (-self.sprite.sourcerect.w < destx < graphics.screenwidth and
                -self.sprite.sourcerect.h < desty < graphics.screenheight and
                not(self.recover)):
            self.sprite.draw(graphics, destx, desty)
        if self.recover:
            AllSprite.playerrecovery.draw(graphics, int(destx), int(desty))
        for l in self.shotlasers:
            l.draw(graphics, self.sp_laser, self.world.camera)

    # def apply_effect(self, effect):
        # print(effect.effecttype)
        # for socket in self.powerup_sockets:
            # print(socket, effect.effecttype, socket == effect.effecttype)
            # if socket == effect.effecttype:
            # self.powerup_sockets[effect.effecttype].remove(self)
            # self.powerup_sockets[effect.effecttype] = effect
        # effect.apply(self)
        # if effect.time > 0:
            # print("SAUCISSE")
            # self.time_effects[effect] = effect.time

    def apply_effect(self, effect):
        AudioManager.play_sound("powerup")
        if effect.effecttype is not None and effect.effecttype in self.powerup_sockets:
            self.powerup_sockets[effect.effecttype].remove(self)
            self.powerup_sockets.pop(effect.effecttype)
        effect.apply(self)
        self.powerup_sockets[effect.effecttype] = effect
        if effect.time > 0:
            print("BITE")
            self.time_effects[effect] = effect.time


class Laser(object):
    """Represent a laser shot by the player.
    Each laser carry its speed and damage value.
    """

    def __init__(self, x, y, velx=0, vely=-900, damage=8):
        self.hitbox = Rectangle(x, y, 8, 8)
        self.velx = velx  # px/s
        self.vely = vely
        self.damage = damage
        AudioManager.play_sound("laser")

    def update(self, world, delta):
        """Update the position of the laser, test for collisions with ennemies
        and return True if the laser should be removed from the laser list.
        world : surrounding world
        delta : nb of seconds passed since the last update.
        """
        self.hitbox.y += self.vely * delta
        self.hitbox.x += self.velx * delta
        for en in world.active_ennemies:
            if en.hitbox.collide(self.hitbox):  # détection du shield
                en.hit(self)
                return True
        if world.camera.collide(self.hitbox):
            return False
        return True

    def draw(self, graphics, sprite, camera):
        """Draw the laser on screen."""
        destx, desty = worldToScreen(self.hitbox.x, self.hitbox.y, camera)
        angle = cart2pol(self.velx, self.vely) + 90
        sprite.draw_rotated(graphics, round(destx - 5), round(desty), angle)

# TODO Créer un projectile continu


class ContinuousLaser(object):

    def __init__(self, x, y, vel=900, damage=8):
        pass


class EnnemyShip(Ship):
    """Abstract class for ennemy ships."""

    def __init__(self, world, hitbox, sprite, spriteoffsetx=0, spriteoffsety=0):
        super(EnnemyShip, self).__init__(
            world, hitbox, sprite, spriteoffsetx, spriteoffsety)
        self.destroyed = False  # Ship destroyed by a laser shot by the player.
        self.scorevalue = 5
        self.hitpoint = 6

    def update(self, delta):
        super(EnnemyShip, self).update(delta)
        if self.world.playership.hitbox.collide(self.hitbox) and not(self.world.playership.recover):
            self.world.player_hit()

    def activate(self):
        """Return true if the ennemy is activated."""
        if self.world.camera.collide(self.hitbox):
            return True
        return False

    def desactivate(self):
        """Return true if the ennemy should be destroyed.
        It happens when the ennemy get out of the screen without being destroyed.
        """
        if not self.world.camera.collide(self.hitbox):
            return True
        return False

    def hit(self, laser):
        """Called when the ennemy is hit by a player laser."""
        self.hitpoint -= laser.damage
        if self.hitpoint <= 0:
            self.destroyed = True

    def destroy(self):
        """Called when the ennemy is destroyed. Might spawn a bonus."""
        AudioManager.play_sound("explosion2")
        if random.random() < POWERUP_SPAWN_RATE:
            ef = get_random_powerup()()
            hitbox = Rectangle(self.hitbox.x, self.hitbox.y, 32, 32)
            pw = WorldPowerUp(hitbox, ef,
                              random.random() < POWERUP_MYSTERY_RATE)
            self.world.powerups.append(pw)


class Bullet(object):
    """This class represent one of the bullets shot by the ennemies."""

    def __init__(self, x, y, velx, vely, size):
        """
        x : float
        y : float
        velx : int (number of pixels to move the bullet each frame on the x-axis)
        vely : int (number of pixels to move the bullet each frame on the y-axis)
        size : int ([1;3] size of the bullet, 1 = small, 2 = medium, 3 = big)
        """
        self.velx = velx  # px/s
        self.vely = vely  # px/s
        if size == 1:
            self.sprite = AllSprite.bullet_small
            self.hitbox = Rectangle(x, y, 12, 12)
        elif size == 2:
            self.sprite = AllSprite.bullet_medium
            self.hitbox = Rectangle(x, y, 24, 24)
        elif size == 3:
            self.sprite = AllSprite.bullet_big
            self.hitbox = Rectangle(x, y, 36, 36)
        else:
            raise Exception(
                "Bullet size can either be 1, 2 or 3. Size give :" + str(size))

    def update(self, delta, world):
        """Update the bullet's position.
        Return True if the bullet should be removed from the bullet list.
        """
        self.hitbox.x += self.velx * delta
        self.hitbox.y += self.vely * delta
        # test for the extend of the camera for bullets
        if not world.bulletextend.collide(self.hitbox):
            return True
        if world.playership.hitbox.collide(self.hitbox) and not(world.playership.recover):
            world.player_hit()
            return True
        return False

    def draw(self, graphics, camera):
        destx, desty = worldToScreen(self.hitbox.x, self.hitbox.y, camera)
        self.sprite.draw(graphics, int(destx), int(desty))


class JohnCena(EnnemyShip):
    """HELLO...
    ...
    ...
    AND GOODBYE TO ANYONE STANDING IN JOHN CENA'S WAY !!
    """

    def __init__(self, world, hitbox):
        super(JohnCena, self).__init__(world, hitbox, AllSprite.boss_cena)
        self.hitpoint = 1000
        self.scorevalue = 420
        self.shooting = False
        self.lastshot = 0
        self.shootingdelay = 0.08
        self.angle1 = -pi / 6
        self.angle2 = 0
        self.rotationspeed1 = 180
        self.rotationspeed2 = 240

    def activate(self):
        """Return true if the ennemy is activated."""
        if self.world.camera.collide(self.hitbox):
            return True
        return False

    def hit(self, laser):
        """Called when the ennemy is hit by a player laser."""
        if self.shield:
            pass
            # créer un laser identiquer et l'ajouter à self.world...
        else:
            super().hit(self, laser)
        # self.hitpoint -= laser.damage
        # if self.hitpoint <= 0:
            # #AllAudio.boss1[4].pause()
            # #AllAudio.theme1[4].play()
            # self.destroyed = True

    def update(self, delta):
        super(JohnCena, self).update(delta)
        # if AllAudio.boss1[4].time == 0.0:
        # AllAudio.theme1[4].play()
        self.lastshot += delta
        self.angle1 += (pi / 30 + 0.042) * self.rotationspeed1 * delta
        self.angle2 += (pi / 30 + 0.042) * self.rotationspeed2 * delta
        if self.hitbox.y >= self.world.camera.y:
            self.hitbox.y = self.world.camera.y
            self.shooting = True
        if self.shooting and self.lastshot >= self.shootingdelay:
            speed = 300
            size = 2
            x = self.hitbox.x + 118
            y = self.hitbox.y + 94
            b = Bullet(x, y, cos(self.angle1) * speed,
                       abs(sin(self.angle1) * speed) - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(self.angle1 + pi) * speed,
                       abs(sin(self.angle1 + pi) * speed) - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(self.angle2) * speed, sin(self.angle2)
                       * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(self.angle2 + pi / 2) * speed,
                       sin(self.angle2 + pi / 2) * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(self.angle2 + pi) * speed, sin(self.angle2 + pi)
                       * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(self.angle2 + 3 * pi / 2) * speed,
                       sin(self.angle2 + 3 * pi / 2) * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            self.lastshot = 0


class Carrier(EnnemyShip):
    wh = (96, 68)

    def __init__(self, world, hitbox):
        super(Carrier, self).__init__(world, hitbox,
                                      AllSprite.boss_carrier, -413, -400)
        self.hitpoint = 1000
        self.scorevalue = 420
        self.shooting = False
        self.shootingdelay = 0.10
        self.lastshot = 0
        self.spawned = False
        self.shield = True
        self.timeBeforeShield = 0
        self.shieldTime = 6
        self.initSprite = False
        self.rotationspeed = 100
        self.angle = 0
        self.angleDep = pi / 2
        self.rotationspeedDep = 1
        self.settled = False
        self.center = [self.hitbox.x, self.hitbox.y + 100]

    def hit(self, laser):
        if not(self.shield):
            self.hitpoint -= laser.damage
        if self.hitpoint <= 0:
            self.destroyed = True

    def allDestroyed(self):
        res = 0
        for ship in self.world.active_ennemies:
            if isinstance(ship, CarrierDrone):
                res += 1
        if res == 0:
            return True
        return False

    def draw(self, graphics):
        super(Carrier, self).draw(graphics)
        destx, desty = worldToScreen(
            self.hitbox.x, self.hitbox.y, self.world.camera)
        if self.timeBeforeShield >= 2:
            AllSprite.shieldcoming.draw(graphics, int(destx), int(desty))
        elif self.shield:
            AllSprite.shield.draw(graphics, int(destx), int(desty))

    def update(self, delta):
        super(Carrier, self).update(delta)
        self.lastshot += delta
        self.angle += (pi / 30 + 0.042) * self.rotationspeed * delta
        if self.settled or self.hitbox.y >= self.world.camera.y + 300:
            self.center[1] = self.world.camera.y + 200
            self.settled = True
            self.shooting = True
            self.angleDep += delta
            self.hitbox.x = self.center[0] + 100 * cos(self.angleDep)
            self.hitbox.y = self.center[1] + 100 * sin(self.angleDep)
            if self.angleDep >= 2 * pi:
                self.angleDep = 0
            if self.shield == True and self.spawned == False:
                self.world.active_ennemies.append(CarrierDrone(
                    self.world, Rectangle(self.hitbox.x + 200, self.hitbox.y + 60, 19, 27), 0))
                self.world.active_ennemies.append(CarrierDrone(
                    self.world, Rectangle(self.hitbox.x + 200, self.hitbox.y - 120, 19, 27), 0))
                self.world.active_ennemies.append(CarrierDrone(
                    self.world, Rectangle(self.hitbox.x - 100, self.hitbox.y + 60, 19, 27), 1))
                self.world.active_ennemies.append(CarrierDrone(
                    self.world, Rectangle(self.hitbox.x - 100, self.hitbox.y - 120, 19, 27), 1))
                self.spawned = True
        if self.shooting and self.lastshot >= self.shootingdelay:
            self.lastshot = 0
            speed = 300
            size = 2
            x1 = self.hitbox.x - self.sp_offset[0]
            x2 = self.hitbox.x + self.sp_offset[0] + 80
            y = self.hitbox.y + self.hitbox.h
            b = Bullet(x1, y, cos(self.angle) * speed,
                       abs(sin(self.angle) * speed) - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x2, y, cos(self.angle + pi) * speed,
                       abs(sin(self.angle + pi) * speed) - self.world.cameraspeed, size)
            self.world.bullets.append(b)
        if self.spawned:
            if self.allDestroyed() == True:
                self.shield = False
                if self.timeBeforeShield >= self.shieldTime:
                    self.shield = True
                    self.spawned = False
                    self.initSprite = True
                    self.timeBeforeShield = 0
                    AllSprite.shieldcoming.currentframe = 0
                self.timeBeforeShield += delta
        if self.timeBeforeShield > 2:
            AllSprite.shieldcoming.update(delta)
        if self.initSprite:
            AllSprite.shieldcoming.currentframe = 0
            self.initSprite = False


class ElementMenu(EnnemyShip):
    """Potatoïd based enemy created to launch menus"""

    def __init__(self, world, hitbox, action, text):
        super(ElementMenu, self).__init__(
            world, hitbox, AllSprite.potato, -25, -15)
        self.action = action
        self.stop = False
        self.angle = random.random() * (2 * pi)
        self.text = text

    def update(self, delta):
        self.angle += delta * pi
        self.hitbox.y -= (self.world.cameraspeed +
                          cos(self.angle) * 30) * delta

    def hit(self, laser):
        self.action()

    def draw(self, graphics):
        super(ElementMenu, self).draw(graphics)
        x, y = worldToScreen(self.hitbox.x, self.hitbox.y, self.world.camera)
        FontManager.draw_text_centered(graphics,
                                       "rebel",
                                       28,
                                       (255, 255, 255),
                                       self.text,
                                       x + self.hitbox.w / 2, y + self.hitbox.h / 2)


class BasicShit(EnnemyShip):
    """Completely useless ennemy. Doing nothing, at all."""
    wh = (24, 26)

    def __init__(self, world, hitbox):
        super(BasicShit, self).__init__(world, hitbox,
                                        AllSprite.en_basic, spriteoffsetx=0, spriteoffsety=-14)


class CircleShit(EnnemyShip):
    """Ship for tests"""

    def __init__(self, world, hitbox):
        super(CircleShit, self).__init__(world, hitbox, AllSprite.en_bis)
        self.shootingdelay = 20
        self.lastshot = 0
        self.hitpoint = 5
        self.scorevalue = 10
        self.t = 1.5 * pi
        self.r = 100
        self.delta = 0.05
        self.x0 = self.hitbox.x
        self.y0 = self.hitbox.y + 100

    def update(self, delta):
        super(CircleShit, self).update(delta)
        self.lastshot += 1
        if self.hitbox.y >= self.world.camera.y + 30:
            self.hitbox.x = int(self.x0 + self.r * cos(self.t))
            self.hitbox.y = int(self.y0 + self.r * sin(self.t))
            self.t += self.delta
            if self.lastshot >= self.shootingdelay:
                self.lastshot = 0
                x = self.hitbox.x + self.hitbox.w / 2
                y = self.hitbox.y + self.hitbox.h / 2
                b = Bullet(x, y, 0, 400, 1)
                self.world.bullets.append(b)


class StandingEnnemies(EnnemyShip):
    wh = (37, 32)

    def __init__(self, world, hitbox):
        super(StandingEnnemies, self).__init__(world, hitbox, AllSprite.en_bis)
        self.shootingdelay = 2
        self.moving = 0
        self.lastshot = 0
        self.hitpoint = 5
        self.scorevalue = 10
        self.vely = -290

    def update(self, delta):
        super(StandingEnnemies, self).update(delta)
        self.moving += 0.01
        self.velx = 100 * cos(self.moving)
        self.vely = 200 * sin(self.moving) - self.world.cameraspeed
        self.hitbox.x = max(self.hitbox.x, self.world.camera.x)
        self.hitbox.x = min(self.hitbox.x, self.world.camera.x +
                            self.world.camera.w - self.hitbox.w)
        self.hitbox.y = max(self.hitbox.y, self.world.camera.y)
        self.hitbox.y = min(
            self.hitbox.y, self.world.camera.y +
            self.world.camera.h - self.hitbox.h)


class CarrierDrone(EnnemyShip):

    def __init__(self, world, hitbox, nb):
        super(CarrierDrone, self).__init__(
            world, hitbox, AllSprite.drone_carrier)
        self.shootingdelay = 2
        self.lastshot = 0
        self.hitpoint = 10
        self.scorevalue = 10
        self.vely = -290
        self.nb = nb
        self.world = world
        # suggestions
        self.angle = 0
        self.rotationspeed = 1

    def update(self, delta):
        super(CarrierDrone, self).update(delta)
        self.angle += delta * self.rotationspeed
        if self.nb == 0:
            self.velx = 100 * cos(self.angle)
            self.vely = 200 * sin(self.angle) - self.world.cameraspeed
            self.hitbox.x = max(self.hitbox.x, self.world.camera.x)
            self.hitbox.x = min(self.hitbox.x, self.world.camera.x +
                                self.world.camera.w - self.hitbox.w)
            self.hitbox.y = max(self.hitbox.y, self.world.camera.y)
            self.hitbox.y = min(self.hitbox.y, self.world.camera.y +
                                self.world.camera.h - self.hitbox.h)
        else:
            self.velx = -100 * cos(self.angle)
            self.vely = 200 * sin(self.angle) - self.world.cameraspeed
            self.hitbox.x = max(self.hitbox.x, self.world.camera.x)
            self.hitbox.x = min(self.hitbox.x, self.world.camera.x +
                                self.world.camera.w - self.hitbox.w)
            self.hitbox.y = max(self.hitbox.y, self.world.camera.y)
            self.hitbox.y = min(self.hitbox.y, self.world.camera.y +
                                self.world.camera.h - self.hitbox.h)


class AngryBird(EnnemyShip):
    wh = (24, 26)

    def __init__(self, world, hitbox):
        super(AngryBird, self).__init__(world, hitbox, AllSprite.en_parrot)
        self.shootingdelay = 0.3
        self.lastshot = 0
        self.hitpoint = 10
        self.scorevalue = 15

    def update(self, delta):
        super(AngryBird, self).update(delta)
        self.lastshot += delta
        if self.lastshot >= self.shootingdelay:
            self.lastshot = 0
            speed = 600
            playerx = self.world.playership.hitbox.x
            playery = self.world.playership.hitbox.y
            x = self.hitbox.x + self.hitbox.w / 2
            y = self.hitbox.y + self.hitbox.h / 2
            vx = playerx - x
            vy = playery - y
            longueur = sqrt(vx**2 + vy**2)
            vx /= longueur
            vy /= longueur
            b = Bullet(x, y, vx * speed, vy * speed -
                       self.world.cameraspeed, 1)
            self.world.bullets.append(b)


class SmallWall(EnnemyShip):
    wh = (300, 100)
    """An ennemy that is nothing more than a wall."""

    def __init__(self, world, hitbox):
        super(SmallWall, self).__init__(world, hitbox, AllSprite.en_smallwall)

    def hit(self, laser):
        pass


class Rotor(EnnemyShip):
    # wh=()
    """ An ennemy's shooting with low frequency in all direction """

    def __init__(self, world, hitbox):
        super(Rotor, self).__init__(world, hitbox,
                                    AllSprite.en_rotor, -15, 30)
        self.lastshot = 0
        self.shootingdelay = 2
        self.angleDep = 0
        self.settled = False
        self.hitpoint = 10
        self.o = self.hitbox.x

    def update(self, delta):
        super(Rotor, self).update(delta)
        self.lastshot += delta
        if self.hitbox.y > self.world.camera.y + 300:
            self.settled = True
        if self.settled == True:
            self.angleDep += delta
            self.hitbox.y = (250 * sin(self.angleDep * 0.5 * pi)) + self.world.camera.y + 300
        if self.lastshot >= self.shootingdelay:
            self.lastshot = 0
            speed = 300
            size = 2
            x = self.hitbox.x - self.sp_offset[0]
            y = self.hitbox.y + self.sp_offset[1]
            b = Bullet(x, y, cos(pi / 4) * speed,
                       abs(sin(pi / 4) * speed) - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(3 * pi / 4) * speed,
                       abs(sin(3 * pi / 4) * speed), size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(-3 * pi / 4) * speed,
                       sin(-3 * pi / 4) * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)
            b = Bullet(x, y, cos(-pi / 4) * speed,
                       sin(-pi / 4) * speed - self.world.cameraspeed, size)
            self.world.bullets.append(b)


def generate_level(world, graphics):
    """Generate opponents.
    Return a file in list format. Head of the list is represent the first
    ennemy of the level.
    """
    # Coordinates generation
    #world.theme = AllAudio.theme1
    coords = []
    for y in range(0, 2500, 25):
        coords.append((y % 1024, -y))
    res = []
    # ship construction
    for coord in coords:
        hitbox = Rectangle(coord[0], coord[1], 24, 26)
        res.append(BasicShit(world, hitbox))
    coords = []
    for i in range(10):
        if i % 2 == 0:
            coords.append((50, -2600 - i * 200))
        else:
            coords.append((SCREEN_WIDTH - 50, -2600 - i * 300))
    for coord in coords:
        hitbox = Rectangle(coord[0], coord[1], 24, 26)
        res.append(AngryBird(world, hitbox))
    # boss
    hitbox = Rectangle(1024 / 2 - 289 / 2, -6000, 289, 300)
    res.append(JohnCena(world, hitbox))
    return sorted(res, key=lambda en: en.hitbox.y, reverse=True)


def generate_level2(world, graphics):
    # Coordinates generation
    coords = []
    for y in range(0, 2500, 25):
        coords.append((y % 1024, -y))
    res = []
    # ship construction
    for coord in coords:
        hitbox = Rectangle(coord[0], coord[1], 24, 26)
        res.append(BasicShit(world, hitbox))
    coords = []
    for i in range(10):
        if i % 2 == 0:
            coords.append((50, -2600 - i * 200))
        else:
            coords.append((SCREEN_WIDTH - 50, -2600 - i * 300))
    for coord in coords:
        hitbox = Rectangle(coord[0], coord[1], 24, 26)
        res.append(AngryBird(world, hitbox))
    coords = []
    for i in range(0, 3000, 500):
        coords.append((250, -i))
        coords.append((SCREEN_WIDTH - 250, -i))
        coords.append((SCREEN_WIDTH // 2, -i - 100))
    for coord in coords:
        hitbox = Rectangle(coord[0], coord[1], 37, 32)
        res.append(StandingEnnemies(world, hitbox))
    # boss
    hitbox = Rectangle(480, -6000, 96, 68)
    res.append(Carrier(world, hitbox))
    return sorted(res, key=lambda en: en.hitbox.y, reverse=True)


def generate_level3(world, graphics):
    res = []
    # hitbox = Rectangle(470, -700, 80, 60)
    # res.append(Rotor(world, hitbox))
    #hitbox = Rectangle(470, -700, 96, 68)
    #res.append(Carrier(world, hitbox))
    from boss3 import Boss3
    hitbox = Rectangle(300, -500, 300, 300)
    res.append(Boss3(world, hitbox))
    return sorted(res, key=lambda en: en.hitbox.y, reverse=True)
