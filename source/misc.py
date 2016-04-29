# module contenant diverses fonctions

from math import *
import sdl2
from sprite import Sprite
from sdl2 import SDL_Delay



def collide(a, b):
    """
    Fonction qui prend a et b en paramètres (deux objets sdl2.SDL_Rect) et qui
    retourne un booléen, True si a et b sont superposés ou False s'ils ne le sont
    pas
    """
    if b.x >= a.x + a.w or b.x + b.w <= a.x or b.y >= a.y + a.h or b.y + b.h <= a.y:
        return False
    return True


def worldToScreen(x, y, camera):
    return (x - camera.x, y - camera.y)


class Rectangle(object):

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    def collide(self, b):
        """
        Fonction qui prend a et b en paramètres (deux objets Rectangle) et qui
        retourne un booléen, True si a et b sont superposés ou False s'ils ne le sont
        pas
        """
        if b.x >= self.right or b.right <= self.x or b.y >= self.bottom or b.bottom <= self.y:
            return False
        return True


class DebugFont(object):

    def __init__(self, graphics):
        self.sp_characters = {}
        x, y = 0, 0
        self.w, self.h = 6, 9
        for c in "0123456789":
            sp = Sprite(graphics, "ressources/debug_font.png", x, y, self.w, self.h)
            self.sp_characters[c] = sp
            x += self.w
        y += self.h
        x = 0
        for c in "ABCDEFGHIJKLM":
            sp = Sprite(graphics, "ressources/debug_font.png", x, y, self.w, self.h)
            self.sp_characters[c] = sp
            x += self.w
        y += self.h
        x = 0
        for c in "NOPQRSTUVWXYZ":
            sp = Sprite(graphics, "ressources/debug_font.png", x, y, self.w, self.h)
            self.sp_characters[c] = sp
            x += self.w
        y += self.h
        x = 0
        for c in ",.;:/%\"-":
            sp = Sprite(graphics, "ressources/debug_font.png", x, y, self.w, self.h)
            self.sp_characters[c] = sp
            x += self.w

    def draw_text(self, graphics, text, x, y):
        """Draw a text at the specified position."""
        for c in text:
            if c in self.sp_characters:
                self.sp_characters[c].draw(graphics, x, y)
            x += self.w


class Clock(object):
    """A clock object is used to limit the number of frame rendered by second.
    usage for 60 loop iterations per second:
    clock = Clock(60)
    while ... :
        ...
        clock.tick()
    """

    def __init__(self, fps=60):
        self.prev = 0
        self.now = sdl2.SDL_GetPerformanceCounter()
        self.freq = sdl2.SDL_GetPerformanceFrequency()
        self.fps = fps

    def tick(self):
        """Called once per main loop iteration. Make sure enough time has passed
        before the next iteration and return the number of seconds passed since
        the last time tick() ended (the delta value).
        """
        self.now = sdl2.SDL_GetPerformanceCounter()
        while self.now - self.prev < self.freq / self.fps:
            self.now = sdl2.SDL_GetPerformanceCounter()
            SDL_Delay(1)
        delta = (self.now - self.prev) / self.freq
        self.prev = self.now
        return delta

class Score(object):

    def __init__(self):
        cnt = load_score('ressources/score/story_score.txt')
        points = [int(i) for i in cnt[0]]
        name = cnt[1]
        self.rank = list(zip(points, name))

    def save(self):
        cnt = open('ressources/score/story_score.txt', 'w')
        line = ""
        x, y = [i[0] for i in self.rank], [i[1] for i in self.rank]
        for i in range(len(x)):
            line += str(x[i])
            if i != len(x)-1:
                line += ","
        line += " "
        for i in range(len(y)):
            line += y[i]
            if i != len(y)-1:
                line += ","
        cnt.write(line)

    def add_score(self, score, name="Jhon_Doe"):

        self.rank += [(score, name)]
        self.rank = sorted(self.rank, reverse=True)
        self.rank.pop()

def load_score(fle):
    cnt = open(fle).readline().split()
    return (cnt[0].split(","), cnt[1].split(","))

def cart2pol(x, y):
    if x == 0:
        if y > 0: angle = 90
        else: angle = -90
    elif y == 0:
        if x > 0: angle = 0
        else: angle = 180
    else:
        p = sqrt(x*x + y*y)
        cost = x / p
        sint = y / p
        tant = sint / cost
        angle = degrees(atan(tant))
    return angle


if __name__ == "__main__":
    c = Clock(10)
    while True:
        c.tick()
