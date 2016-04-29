
import sdl2
import sdl2.ext


class Graphics():

    def __init__(self, screenwidth, screenheight):
        self.window = sdl2.SDL_CreateWindow(b"Rugliek",
                                            sdl2.SDL_WINDOWPOS_UNDEFINED,
                                            sdl2.SDL_WINDOWPOS_UNDEFINED,
                                            screenwidth,
                                            screenheight,
                                            sdl2.SDL_WINDOW_SHOWN)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, 0)
        self.spritesheets = {}
        self.screenwidth = screenwidth
        self.screenheight = screenheight

    def __del__(self):
        for spritesheet in self.spritesheets.values():
            sdl2.SDL_DestroyTexture(spritesheet)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)

    def load_image(self, filepath):
        spritesheet = self.spritesheets.get(filepath)
        if not spritesheet:
            surface = sdl2.ext.load_image(filepath)
            spritesheet = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
            self.spritesheets[filepath] = spritesheet
            sdl2.SDL_FreeSurface(surface)
        return spritesheet

    def blit_surface(self, source, srcRect, dstRect):
        # Dont blit not visible things.
        if dstRect is None:
            sdl2.SDL_RenderCopy(self.renderer, source, srcRect, None)
            return

        if dstRect.x > self.screenwidth or dstRect.y > self.screenheight or \
                dstRect.x + dstRect.w < 0 or dstRect.y + dstRect.h < 0:
            return
        sdl2.SDL_RenderCopy(self.renderer, source, srcRect, dstRect)

    def blit_surface_rotated(self, source, srcRect, dstRect, angle):
        if dstRect.x > self.screenwidth or dstRect.y > self.screenheight or \
                dstRect.x + dstRect.w < 0 or dstRect.y + dstRect.h < 0:
            return
        sdl2.SDL_RenderCopyEx(self.renderer, source, srcRect, dstRect, angle, None, 0)



    # def blit_surface_roto(self, source, srcRect, dstRect, angle):
        # surface = sdl2.ext.subsurface(source, srcRect)
        # surface2 = gfx.rotozoomSurface(source, angle, 1, 0)

        # if dstRect.x > self.screenwidth or dstRect.y > self.screenheight or \
                # dstRect.x + dstRect.w < 0 or dstRect.y + dstRect.h < 0:
            # return
        # sdl2.SDL_RenderCopy(self.renderer, None, srcRect, dstRect)


    def clear(self):
        sdl2.SDL_RenderClear(self.renderer)

    def flip(self):
        sdl2.SDL_RenderPresent(self.renderer)
