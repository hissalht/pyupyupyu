from math import pi, cos, sin
from random import randint

from ship import EnnemyShip, Bullet, SCREEN_WIDTH, SCREEN_HEIGHT
from sprite import AllSprite


class BossPattern(object):

    def __init__(self):
        pass

    def update(self, ship, delta):
        pass

    def initship(self, ship):
        pass


class BossPatternFirst(BossPattern):

    def __init__(self):
        self.shootingdelay = 0.4
        self.nextshot = 0
        self.bpw = 40  # bullets per waves
        self.bspeed = 100  # bullet speed
        self.sangle = 0  # starting angle

    def initship(self, ship):
        ship.vely = -ship.world.cameraspeed

    def update(self, ship, delta):
        self.nextshot -= delta
        self.sangle += delta / 5
        if self.nextshot <= 0:
            self.nextshot = self.shootingdelay
            for i in range(self.bpw):
                angle = self.sangle + i * (2 * pi / self.bpw)
                vx = cos(angle) * self.bspeed
                vy = sin(angle) * self.bspeed - ship.world.cameraspeed
                b = Bullet(ship.hitbox.x + ship.hitbox.w / 2,
                           ship.hitbox.y + ship.hitbox.h / 2,
                           vx, vy, 2)
                ship.world.bullets.append(b)


class BossPatternSecond(BossPattern):

    def __init__(self):
        self.posangle = 0
        self.mspeed = 2  # movement SPEED
        self.wavedelay = .4
        self.nextwave = 0
        self.bpw = 10
        self.wavewidth = 300
        self.initialwaittime = 6
        self.waittime = 0

    def update(self, ship, delta):
        self.waittime += delta
        self.posangle += delta * self.mspeed
        t = sin(self.posangle)
        ship.hitbox.x = SCREEN_WIDTH / 2 + t * (SCREEN_WIDTH / 2) - ship.hitbox.w / 2
        self.nextwave -= delta
        if self.nextwave <= 0 and self.waittime >= self.initialwaittime:
            self.nextwave = self.wavedelay
            for i in range(self.bpw):
                mx = self.wavewidth / self.bpw * i
                vy = randint(350, 500) - ship.world.cameraspeed
                vx = 0
                b = Bullet(ship.hitbox.x + mx,
                           ship.hitbox.y + ship.hitbox.h,
                           vx, vy, 2)
                ship.world.bullets.append(b)

    def initship(self, ship):
        ship.vely = -ship.world.cameraspeed
        self.waittime = 0
        pass


class Boss3(EnnemyShip):
    wh = (300, 300)

    def __init__(self, world, hitbox):
        super().__init__(world, hitbox, AllSprite.en_boss3)
        self.hitpoint = 10000
        self.scorevalue = 7777
        self.invicible = False
        self.inactive = True
        self.patterns = [BossPatternFirst(), BossPatternSecond()]
        self.pindex = 0
        self.ptimer = 10
        self.nextpattern = self.ptimer

    def update(self, delta):
        super().update(delta)
        if self.inactive and self.hitbox.y >= self.world.camera.y:
            self.inactive = False
            self.patterns[self.pindex % len(self.patterns)].initship(self)
        if not self.inactive:
            self.nextpattern -= delta
            if self.nextpattern <= 0:
                self.nextpattern = self.ptimer
                self.pindex += 1
                self.patterns[self.pindex % len(self.patterns)].initship(self)
            self.patterns[self.pindex % len(self.patterns)].update(self, delta)
