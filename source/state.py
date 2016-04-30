from sdl2 import *
import sdl2.ext as ext
from misc import Clock
import sys
from random import randint

from graphics import Graphics
from sprite import *
from world import *
from level import *
from misc import Score, Rectangle, DebugFont, Clock
from ship import PlayerShip, ElementMenu, generate_level, generate_level2, generate_level3
from font import FontManager

from powerups import FiringSpeedEffect, RandomDirectionEffect, DoubleLaserEffect

from audio import load_audio, AudioManager


class State(object):
    """This class is used to build the differents state of the game (menu state,
    gameplay state, etc).
    """
    __nbinstances = 0

    def __init__(self, graphics, **kwargs):
        State.__nbinstances += 1
        self.graphics = graphics
        self.framerate = kwargs.get("framerate", 60)
        self.name = kwargs.get("name", "State%d" % State.__nbinstances)
        self.clock = Clock(self.framerate)
        self.running = True
        self.pause = False
        self.score = Score()

    def __del__(self):
        State.__nbinstances -= 1

    def run(self):
        """Main loop of the state."""
        delta = self.clock.tick()
        while self.running:
            delta = self.clock.tick()
            for event in ext.get_events():
                self.handle_event(event)
            self.update(delta)
            self.draw()

    def update(self, delta):
        """Variables are updated here (positions, timer, etc)."""
        raise Exception("update() method have to be overriden")
        pass

    def draw(self):
        """The state is drawn here."""
        raise Exception("draw() method have to be overriden")
        pass

    def handle_event(self, event):
        """The events are handled here. This method is called every time an
        event occur.
        """
        raise Exception("handle_event() method have to be overriden")
        pass

    def reset(self):
        """Called to reset the state."""
        raise Exception("reset() method have to be overriden")
        pass


class InfiniteGame(State):

    def __init__(self, graphics):
        super().__init__(graphics, framerate=60, name="game")
        self.world = World()
        # Playership creation
        playership_hitbox = Rectangle(SCREEN_WIDTH / 2 - 9, 740, 2, 2)
        self.playership = PlayerShip(self.world, playership_hitbox, AllSprite.player,
                                     AllSprite.laser_basic, spriteoffsetx=-14, spriteoffsety=-5)
        self.world.playership = self.playership
        # Player's shooting
        self.shooting = False
        # Level generation
        self.currentlevel = 0
        level = Level(self.currentlevel, self.world, 0, 20)
        #self.world.standby_ennemies = generate_level3(self.world, graphics)
        self.world.standby_ennemies = level.level
        # theme play
        # AudioManager.play_music("theme")
        # debug display
        self.debugfont = DebugFont(graphics)
        self.debug_info = True

        self.test_effect1 = DoubleLaserEffect()
        self.test_effect2 = RandomDirectionEffect()

        self.timerEnd = 0

    def restart(self):
        self.wordl = World()
        playership_hitbox = Rectangle(SCREEN_WIDTH / 2 - 9, 740, 18, 18)
        self.playership = PlayerShip(self.world, playership_hitbox, AllSprite.player,
                                     AllSprite.laser_basic, spriteoffsetx=-6, spriteoffsety=-4)
        self.world.playership = self.playership
        self.world.standby_ennemies = generate_level(self.world, graphics)

    def __del__(self):
        super().__del__()
        # AllAudio.pause(self.world.theme)

    def update(self, delta):
        if self.pause:
            AudioManager.set_music_volume(0.1)
            return
        if self.shooting:
            self.world.playership.shoot()
        if not(self.pause):
            AudioManager.set_music_volume(1)
        self.world.update(delta)
        self.running = self.running and not self.world.gameover
        self.debug_fps = 1 / delta
        # new ennemies
        if self.world.active_ennemies == [] and self.world.standby_ennemies == [] and self.currentlevel < 4:
            self.currentlevel += 1
            level = Level(self.currentlevel, self.world, self.world.camera.y, 20)
            self.world.standby_ennemies = level.level
        elif self.world.active_ennemies == [] and self.world.standby_ennemies == [] and self.currentlevel == 4:
            level = Level(self.currentlevel, self.world, self.world.camera.y, 20)
            self.world.standby_ennemies = level.level

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            sys.exit("Closing the game...")
            self.running = False
        elif event.type == SDL_KEYDOWN and event.key.repeat == 0:
            key = event.key.keysym.sym
            if key == SDLK_UP:
                self.world.playership.vely = -self.playership.maxspeed
            elif key == SDLK_DOWN:
                self.world.playership.vely = self.playership.maxspeed
            elif key == SDLK_LEFT:
                self.world.playership.velx = -self.playership.maxspeed
            elif key == SDLK_RIGHT:
                self.world.playership.velx = self.playership.maxspeed
            elif key == SDLK_SPACE:
                self.shooting = True
            elif key == SDLK_p and self.playership.shootingdelay > 0:
                self.playership.shootingdelay /= 2
            elif key == SDLK_m:
                self.playership.shootingdelay *= 2
            elif key == SDLK_ESCAPE:
                self.running = False
            elif key == SDLK_F1:
                self.debug_info = not self.debug_info
            elif key == SDLK_F2:
                # self.pause = not self.pause
                AudioManager.play_sound("bleep")
                pauseState = Pause(self.graphics, self)
                pauseState.run()
                AudioManager.play_sound("bleep")
                self.clock.tick()
            elif key == SDLK_e:
                self.test_effect1.apply(self.playership)
            elif key == SDLK_r:
                self.test_effect2.apply(self.playership)
        elif event.type == SDL_KEYUP:
            key = event.key.keysym.sym
            if key == SDLK_RIGHT:
                if self.playership.velx > 0:
                    self.playership.velx = 0
            elif key == SDLK_LEFT:
                if self.playership.velx < 0:
                    self.playership.velx = 0
            elif key == SDLK_DOWN:
                if self.playership.vely > 0:
                    self.playership.vely = 0
            elif key == SDLK_UP:
                if self.playership.vely < 0:
                    self.playership.vely = 0
            elif key == SDLK_SPACE:
                self.shooting = False

    def draw(self):
        self.graphics.clear()
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536))
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536) + 1536)
        self.world.draw(self.graphics)
        if self.debug_info:
            self.debugfont.draw_text(
                self.graphics, "FPS : %d" % self.debug_fps, 10, 10)
            self.debugfont.draw_text(
                self.graphics, "CAM Y : %d" % self.world.camera.y, 10, 20)
            self.debugfont.draw_text(
                self.graphics, "SCORE : %d" % self.world.score, 10, 30)
            self.debugfont.draw_text(
                self.graphics, "LIVES : %d" % self.world.life, 10, 40)
            self.debugfont.draw_text(self.graphics, "STANDBY ENNEMIES : %d" %
                                     len(self.world.standby_ennemies), 10, 50)
            self.debugfont.draw_text(self.graphics, "ACTIVE ENNEMIES : %d" %
                                     len(self.world.active_ennemies), 10, 60)
            self.debugfont.draw_text(
                self.graphics, "SPEED : %d" % self.world.playership.maxspeed, 10, 90)
        # FontManager.draw_text(self.graphics, "rebel", 16, (255, 255, 255), str(int(self.world.camera.y)), 300, 500)
        # FontManager.draw_text(self.graphics, "dejavu", 20, (255, 255, 255), str(int(self.world.camera.y)), 300, 400)
        FontManager.draw_text(self.graphics, "rebel", 28,
                              (255, 255, 255),
                              "Score : " + str(self.world.score),
                              10, SCREEN_HEIGHT - 40)
        FontManager.draw_text(self.graphics, "rebel", 28,
                              (255, 255, 255),
                              "x" + str(self.world.score_multiplier),
                              10, SCREEN_HEIGHT - 80)
        if self.world.standby_ennemies == [] and self.world.active_ennemies == [] and self.world.bullets == []:
            FontManager.draw_text_centered(graphics,
                                           "rebel",
                                           28,
                                           (255, 255, 255),
                                           "END IS NEAR",
                                           SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.graphics.flip()


class StoryGame(State):

    def __init__(self, graphics):
        super().__init__(graphics, framerate=60, name="game")
        self.world = World()
        # Playership creation
        playership_hitbox = Rectangle(SCREEN_WIDTH / 2 - 9, 740, 2, 2)
        self.playership = PlayerShip(self.world, playership_hitbox, AllSprite.player,
                                     AllSprite.laser_basic, spriteoffsetx=-14, spriteoffsety=-5)
        self.world.playership = self.playership
        # Player's shooting
        self.shooting = False
        # Level generation
        level = Level(4, self.world)
        level.makelevel(10)
        ##self.world.standby_ennemies = generate_level3(self.world, graphics)
        self.world.standby_ennemies = level.level
        # theme play
        # AudioManager.play_music("theme")
        # debug display
        self.debugfont = DebugFont(graphics)
        self.debug_info = True

        self.test_effect1 = DoubleLaserEffect()
        self.test_effect2 = RandomDirectionEffect()

        self.timerEnd = 0

    def restart(self):
        self.wordl = World()
        playership_hitbox = Rectangle(SCREEN_WIDTH / 2 - 9, 740, 18, 18)
        self.playership = PlayerShip(self.world, playership_hitbox, AllSprite.player,
                                     AllSprite.laser_basic, spriteoffsetx=-6, spriteoffsety=-4)
        self.world.playership = self.playership
        self.world.standby_ennemies = generate_level(self.world, graphics)

    def __del__(self):
        super().__del__()
        # AllAudio.pause(self.world.theme)

    def update(self, delta):
        if self.pause:
            AudioManager.set_music_volume(0.1)
            return
        if self.shooting:
            self.world.playership.shoot()
        if not(self.pause):
            AudioManager.set_music_volume(1)
        self.world.update(delta)
        self.running = self.running and not self.world.gameover
        self.debug_fps = 1 / delta
        if self.world.standby_ennemies == [] and self.world.active_ennemies == [] and self.world.bullets == []:
            self.timerEnd += delta
            if self.timerEnd >= 3:
                self.score.add_score(self.world.score)
                self.score.save()
                self.running = False

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            sys.exit("Closing the game...")
            self.running = False
        elif event.type == SDL_KEYDOWN and event.key.repeat == 0:
            key = event.key.keysym.sym
            if key == SDLK_UP:
                self.world.playership.vely = -self.playership.maxspeed
            elif key == SDLK_DOWN:
                self.world.playership.vely = self.playership.maxspeed
            elif key == SDLK_LEFT:
                self.world.playership.velx = -self.playership.maxspeed
            elif key == SDLK_RIGHT:
                self.world.playership.velx = self.playership.maxspeed
            elif key == SDLK_SPACE:
                self.shooting = True
            elif key == SDLK_p and self.playership.shootingdelay > 0:
                self.playership.shootingdelay /= 2
            elif key == SDLK_m:
                self.playership.shootingdelay *= 2
            elif key == SDLK_ESCAPE:
                self.running = False
            elif key == SDLK_F1:
                self.debug_info = not self.debug_info
            elif key == SDLK_F2:
                # self.pause = not self.pause
                AudioManager.play_sound("bleep")
                pauseState = Pause(self.graphics, self)
                pauseState.run()
                AudioManager.play_sound("bleep")
                self.clock.tick()
            elif key == SDLK_e:
                self.test_effect1.apply(self.playership)
            elif key == SDLK_r:
                self.test_effect2.apply(self.playership)
        elif event.type == SDL_KEYUP:
            key = event.key.keysym.sym
            if key == SDLK_RIGHT:
                if self.playership.velx > 0:
                    self.playership.velx = 0
            elif key == SDLK_LEFT:
                if self.playership.velx < 0:
                    self.playership.velx = 0
            elif key == SDLK_DOWN:
                if self.playership.vely > 0:
                    self.playership.vely = 0
            elif key == SDLK_UP:
                if self.playership.vely < 0:
                    self.playership.vely = 0
            elif key == SDLK_SPACE:
                self.shooting = False

    def draw(self):
        self.graphics.clear()
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536))
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536) + 1536)
        self.world.draw(self.graphics)
        if self.debug_info:
            self.debugfont.draw_text(
                self.graphics, "FPS : %d" % self.debug_fps, 10, 10)
            self.debugfont.draw_text(
                self.graphics, "CAM Y : %d" % self.world.camera.y, 10, 20)
            self.debugfont.draw_text(
                self.graphics, "SCORE : %d" % self.world.score, 10, 30)
            self.debugfont.draw_text(
                self.graphics, "LIVES : %d" % self.world.life, 10, 40)
            self.debugfont.draw_text(self.graphics, "STANDBY ENNEMIES : %d" %
                                     len(self.world.standby_ennemies), 10, 50)
            self.debugfont.draw_text(self.graphics, "ACTIVE ENNEMIES : %d" %
                                     len(self.world.active_ennemies), 10, 60)
            self.debugfont.draw_text(
                self.graphics, "SPEED : %d" % self.world.playership.maxspeed, 10, 90)
        # FontManager.draw_text(self.graphics, "rebel", 16, (255, 255, 255), str(int(self.world.camera.y)), 300, 500)
        # FontManager.draw_text(self.graphics, "dejavu", 20, (255, 255, 255), str(int(self.world.camera.y)), 300, 400)
        FontManager.draw_text(self.graphics, "rebel", 28,
                              (255, 255, 255),
                              "Score : " + str(self.world.score),
                              10, SCREEN_HEIGHT - 40)
        FontManager.draw_text(self.graphics, "rebel", 28,
                              (255, 255, 255),
                              "x" + str(self.world.score_multiplier),
                              10, SCREEN_HEIGHT - 80)
        if self.world.standby_ennemies == [] and self.world.active_ennemies == [] and self.world.bullets == []:
            FontManager.draw_text_centered(graphics,
                                           "rebel",
                                           28,
                                           (255, 255, 255),
                                           "END IS NEAR",
                                           SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.graphics.flip()


class Menu(State):

    def __init__(self, graphics):
        super().__init__(graphics, framerate=60, name="menu")
        self.world = World()
        # Playership creation
        playership_hitbox = Rectangle(SCREEN_WIDTH / 2 - 9, 740, 18, 18)
        self.playership = PlayerShip(self.world, playership_hitbox, AllSprite.player,
                                     AllSprite.laser_basic, spriteoffsetx=-6, spriteoffsety=-4)
        self.world.cameraspeed = 100
        self.world.playership = self.playership
        self.shooting = False

        def launchGame():
            playState = Play(self.graphics, self)
            playState.run()
            self.clock.tick()
            self.reset()

            #game = Game(graphics)
            # game.run()
            # self.clock.tick()
            # self.reset()

        def launchHi():
            hi = High_Score(graphics)
            hi.run()
            self.clock.tick()
            self.reset()

        def launchOpt():
            pass

        # Elements of the menu creation
        hitboxPlay = Rectangle(55, int(SCREEN_HEIGHT / 2), 145, 100)
        hitboxHi = Rectangle(315, int(SCREEN_HEIGHT / 2), 145, 100)
        hitboxOptions = Rectangle(565, int(SCREEN_HEIGHT / 2), 145, 100)
        hitboxExit = Rectangle(815, int(SCREEN_HEIGHT / 2), 145, 100)
        self.world.standby_ennemies.append(ElementMenu(
            self.world, hitboxPlay, launchGame, "Play"))
        self.world.standby_ennemies.append(ElementMenu(
            self.world, hitboxHi, launchHi, "Hi-Score"))
        self.world.standby_ennemies.append(ElementMenu(
            self.world, hitboxOptions, launchOpt, "Options"))
        self.world.standby_ennemies.append(ElementMenu(
            self.world, hitboxExit, self.stop, "Exit"))

    def reset(self):
        self.world.camera.y = 0
        for i in self.world.active_ennemies:
            i.hitbox.y = int(SCREEN_HEIGHT / 2)
        self.playership.hitbox.x = SCREEN_WIDTH / 2 - 9
        self.playership.hitbox.y = 740
        self.shooting = False

    def update(self, delta):
        if self.shooting:
            self.world.playership.shoot()
        self.world.update(delta)
        self.running = self.running and not self.world.gameover
        self.debug_fps = 1 / delta

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            self.running = False
        elif event.type == SDL_DROPFILE:
            self.clock.tick()
        elif event.type == SDL_KEYDOWN and event.key.repeat == 0:
            if event.key.keysym.sym == SDLK_UP:
                self.world.playership.vely = -self.playership.maxspeed
            elif event.key.keysym.sym == SDLK_DOWN:
                self.world.playership.vely = self.playership.maxspeed
            elif event.key.keysym.sym == SDLK_LEFT:
                self.world.playership.velx = -self.playership.maxspeed
            elif event.key.keysym.sym == SDLK_RIGHT:
                self.world.playership.velx = self.playership.maxspeed
            elif event.key.keysym.sym == SDLK_SPACE:
                self.shooting = True
            elif event.key.keysym.sym == SDLK_p and self.playership.shootingdelay > 0:
                self.playership.shootingdelay /= 2
            elif event.key.keysym.sym == SDLK_m:
                self.playership.shootingdelay *= 2
            elif event.key.keysym.sym == SDLK_ESCAPE:
                self.running = False
            elif event.key.keysym.sym == SDLK_F1:
                self.debug_info = not self.debug_info
        elif event.type == SDL_KEYUP:
            if event.key.keysym.sym == SDLK_RIGHT:
                if self.playership.velx > 0:
                    self.playership.velx = 0
            elif event.key.keysym.sym == SDLK_LEFT:
                if self.playership.velx < 0:
                    self.playership.velx = 0
            elif event.key.keysym.sym == SDLK_DOWN:
                if self.playership.vely > 0:
                    self.playership.vely = 0
            elif event.key.keysym.sym == SDLK_UP:
                if self.playership.vely < 0:
                    self.playership.vely = 0
            elif event.key.keysym.sym == SDLK_SPACE:
                self.shooting = False

    def draw(self):
        self.graphics.clear()
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536))
        AllSprite.bg.draw(self.graphics, -int(self.world.camera.x), -
                          int(self.world.camera.y % 1536) + 1536)
        AllSprite.title.draw(self.graphics, int(
            SCREEN_WIDTH / 2 - AllSprite.title.sourcerect.w / 2), 50)
        self.world.draw(self.graphics)
        self.graphics.flip()

    def stop(self):
        self.running = False


class Play(State):

    def __init__(self, graphics, gamestate):
        super().__init__(graphics, framerate=30, name="play")
        graphics.clear()

        bg = SDL_GetWindowSurface(graphics.window)
        # black = SDL_Surface(
        # SDL_FillRect(bg, None, SDL_Color(
        self.background = SDL_CreateTextureFromSurface(self.graphics.renderer, bg)
        self.gamestate = gamestate

        self.menu = ["Story", "Infinite", "Quit"]
        self.menuindex = 0

    def draw(self):
        # self.graphics.blit_surface(self.background, None, None)
        for i in range(len(self.menu)):
            if self.menuindex % len(self.menu) == i:
                FontManager.draw_text_centered(self.graphics, "rebel", 28,
                                               (randint(0, 255), randint(0, 255), randint(0, 255)),
                                               self.menu[i],
                                               SCREEN_WIDTH / 2, 250 + 150 * i)
            else:
                FontManager.draw_text_centered(self.graphics, "rebel", 28,
                                               (180, 180, 180),
                                               self.menu[i],
                                               SCREEN_WIDTH / 2, 250 + 150 * i)
        self.graphics.flip()

    def update(self, delta):
        pass

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key == SDLK_DOWN:
                self.menuindex += 1
            elif key == SDLK_UP:
                self.menuindex -= 1
            elif key == SDLK_ESCAPE:
                self.running = False
            elif key == SDLK_RETURN:
                self.select()

    def select(self):
        if self.menu[self.menuindex % len(self.menu)] == "Story":
            game = StoryGame
            game.run()
            self.running = False
            return
        elif self.menu[self.menuindex % len(self.menu)] == "Infinite":
            game = InfiniteGame(graphics)
            game.run()
            self.running = False
            return
        elif self.menu[self.menuindex % len(self.menu)] == "Quit":
            self.running = False
            return


class Pause(State):

    def __init__(self, graphics, gamestate):
        super().__init__(graphics, framerate=30, name="pause")
        bg = SDL_GetWindowSurface(graphics.window)
        # black = SDL_Surface(
        # SDL_FillRect(bg, None, SDL_Color(
        self.background = SDL_CreateTextureFromSurface(self.graphics.renderer, bg)
        self.gamestate = gamestate

        self.menu = ["Continue", "Quit"]
        self.menuindex = 0

    def draw(self):
        # self.graphics.blit_surface(self.background, None, None)
        for i in range(len(self.menu)):
            if self.menuindex % len(self.menu) == i:
                FontManager.draw_text_centered(self.graphics, "rebel", 28,
                                               (randint(0, 255), randint(0, 255), randint(0, 255)),
                                               self.menu[i],
                                               SCREEN_WIDTH / 2, 250 + 150 * i)
            else:
                FontManager.draw_text_centered(self.graphics, "rebel", 28,
                                               (180, 180, 180),
                                               self.menu[i],
                                               SCREEN_WIDTH / 2, 250 + 150 * i)
        self.graphics.flip()

    def update(self, delta):
        pass

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key == SDLK_DOWN:
                self.menuindex += 1
            elif key == SDLK_UP:
                self.menuindex -= 1
            elif key == SDLK_ESCAPE:
                self.running = False
            elif key == SDLK_RETURN:
                self.select()

    def select(self):
        if self.menu[self.menuindex % len(self.menu)] == "Continue":
            self.running = False
            return
        elif self.menu[self.menuindex % len(self.menu)] == "Quit":
            self.gamestate.running = False
            self.running = False
            return


class High_Score(State):

    def __init__(self, graphics):
        super().__init__(graphics, framerate=60, name="high_score")
        self.score = Score()

        self.coords = [(SCREEN_WIDTH / 2, i) for i in range(30, 738, 75)]
        self.graphics.clear()
        for i in range(10):
            txt = str(i + 1) + ": " + str(self.score.rank[i][0]) + "    " + self.score.rank[i][1]
            FontManager.draw_text_centered(graphics,
                                           "rebel",
                                           28,
                                           (255, 255, 255),
                                           txt,
                                           self.coords[i][0], self.coords[i][1])

        self.graphics.flip()

    def reset(self):
        self.world.camera.y = 0

    def update(self, delta):
        pass

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            self.running = False
        elif event.type == SDL_DROPFILE:
            self.clock.tick()
        elif event.type == SDL_KEYDOWN and event.key.repeat == 0:
            if event.key.keysym.sym == SDLK_ESCAPE:
                self.running = False
            elif event.key.keysym.sym == SDLK_F1:
                self.debug_info = not self.debug_info

    def draw(self):
        pass

    def stop(self):
        self.running = False


if __name__ == "__main__":
    ext.init()
    graphics = Graphics(SCREEN_WIDTH, SCREEN_HEIGHT)
    AllSprite.load_sprites(graphics)
    AudioManager.init_audio()
    load_audio()
    FontManager.load_font("ressources/Rebellion.ttf", "rebel", 28)
    FontManager.load_font("ressources/DejaVuSansMono.ttf", "dejavu", 20)
    game = Menu(graphics)
    game.run()
    ext.quit()
