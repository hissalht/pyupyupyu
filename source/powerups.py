from math import cos, sin, radians
from random import randint
from enum import *

# from ship import PlayerShip, Laser
from ship import *
from misc import worldToScreen
from graphics import Graphics


class WorldPowerUp(object):
    """
    Represent a powerup in the world. It links a particular powerup effect
    with an icon in-game.
    """

    def __init__(self, hitbox, effect, mystery=False):
        """Create a new floating powerup object.
        effect : PowerUpEffect
        mystery : If True, a "?" is displayed instead of the effect sprite.
        """
        self.hitbox = hitbox
        self.effect = effect
        self.mystery = mystery

    def draw(self, graphics, camera):
        destx, desty = worldToScreen(self.hitbox.x,
                                     self.hitbox.y,
                                     camera)
        destx = round(destx)
        desty = round(desty)
        if not self.mystery:
            self.effect.sprite.draw(graphics, destx, desty)
        else:
            AllSprite.pow_mystery.draw(graphics, destx, desty)

    def update(self, world, delta):
        self.hitbox.y -= delta * 200
        if world.playership.hitbox.collide(self.hitbox):
            # self.effect.apply(world.playership)
            world.playership.apply_effect(self.effect)
            return True
        if world.camera.collide(self.hitbox):
            return False
        return True


class PowerUpEffect(object):
    """
    Abstract super class for powerup effects. The effect is applied by
    calling the `apply` method and removed by calling the `remove` method.
    """

    def __init__(self, name, sprite, effecttype, time=0):
        self.name = name
        self.sprite = sprite
        self.time = time
        self.effecttype = effecttype

    def apply(self, ship):
        raise Exception("You have to override the apply method")

    def remove(self, ship):
        raise Exception("You have to override the apply method")


class FiringSpeedEffect(PowerUpEffect):
    """Increase the firing speed of the player ship"""

    def __init__(self):
        super().__init__("speed", AllSprite.pow_attackspeed, "weapon")

    def apply(self, ship):
        print("Effect applied")
        ship.shootingdelay /= 2.0

    def remove(self, ship):
        print("Effect removed")
        ship.shootingdelay *= 2.0


class DoubleLaserEffect(PowerUpEffect):
    """Makes the player ship shoot lasers in two different directions."""

    def __init__(self):
        super().__init__("doubleattack", AllSprite.pow_doubleattack, "weapon")
        self.angle = radians(85)  # degrees

    def apply(self, ship):
        self.shoot_backup = ship.shoot_method

        def custom_shoot(cself):
            from ship import Laser
            if cself.lastshot >= cself.shootingdelay:
                velx = cos(self.angle) * 900
                vely = -sin(self.angle) * 900
                x = int(cself.hitbox.x + cself.hitbox.w / 2 + randint(-10, 10))
                y = cself.hitbox.y
                cself.shotlasers.append(Laser(x, y, velx, vely))
                x = int(cself.hitbox.x + cself.hitbox.w / 2 + randint(-10, 10))
                y = cself.hitbox.y
                cself.shotlasers.append(Laser(x, y, -velx, vely))
                cself.lastshot = 0
        ship.shoot_method = custom_shoot

    def remove(self, ship):
        ship.shoot_method = self.shoot_backup


class RandomDirectionEffect(PowerUpEffect):
    """Makes laser go in every direction and increase attack speed for the lulz"""

    def __init__(self):
        super().__init__("death doom", AllSprite.pow_doom, "weapon")

    def apply(self, ship):
        self.shoot_backup = ship.shoot_method

        def custom_shoot(cself):
            from ship import Laser
            if cself.lastshot >= cself.shootingdelay:
                angle = radians(randint(0, 360))
                velx = cos(angle) * 600
                vely = -sin(angle) * 600 - cself.world.cameraspeed
                x = int(cself.hitbox.x + cself.hitbox.w / 2 + randint(-10, 10))
                y = cself.hitbox.y
                cself.shotlasers.append(Laser(x, y, velx, vely))
                cself.lastshot = 0

        ship.shoot_method = custom_shoot
        ship.shootingdelay /= 32

    def remove(self, ship):
        ship.shoot_method = self.shoot_backup
        ship.shootingdelay *= 32


class SlowMovementEffect(PowerUpEffect):
    def __init__(self):
        super().__init__("slow", AllSprite.pow_slow, None, 5)

    def apply(self, ship):
        ship.maxspeed *= 0.33

    def remove(self, ship):
        ship.maxspeed /= 0.33


class MultiplierOneEffect(PowerUpEffect):
    """Add 1 to the score multiplier."""

    def __init__(self):
        super().__init__("bonus1", AllSprite.pow_bonus1, None)

    def apply(self, ship):
        ship.world.score_multiplier += 1


class MultiplierMinusTwoEffect(PowerUpEffect):
    """Sub 2 to the score multiplier."""

    def __init__(self):
        super().__init__("malus2", AllSprite.pow_malus2, None)

    def apply(self, ship):
        ship.world.score_multiplier -= 2


# (rarity factor, effect class)
# Lower rarity factor = rarer effect
POWERUP_LIST = {"speed": [5, FiringSpeedEffect],
                "doubleattack": [5, DoubleLaserEffect],
                "death doom": [5, RandomDirectionEffect],
                "bonus1": [2, MultiplierOneEffect],
                "malus2": [2, MultiplierMinusTwoEffect],
                "slow": [2, SlowMovementEffect]}
POWERUP_RARITY_TOTAL = sum(x[0] for x in POWERUP_LIST.values())
# POWERUP_SPAWN_RATE = 0.05
POWERUP_SPAWN_RATE = 0.05
POWERUP_MYSTERY_RATE = 0.2


def get_random_powerup():
    """Return a random powerup effect class according to its rarity."""
    n = randint(1, POWERUP_RARITY_TOTAL)
    c = 0
    for p in POWERUP_LIST:
        c += POWERUP_LIST[p][0]
        if c >= n:
            return POWERUP_LIST[p][1]


# def test():
    # s, d, dd = 0, 0, 0
    # for x in range(1000):
        # ef = get_random_powerup()
        # if ef is FiringSpeedEffect: s += 1
        # if ef is DoubleLaserEffect: d += 1
        # if ef is RandomDirectionEffect: dd += 1
    # total = s + d + dd
    # print(s/total, d/total, dd/total)
