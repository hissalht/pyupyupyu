
from sdl2 import *
from sdl2.sdlttf import *
import sdl2.ext as ext

from graphics import Graphics


def main():
    ext.init()
    graphics = Graphics(640, 480)

    TTF_Init()
    font = TTF_OpenFont(b"rebel.ttf", 16)
    if(not font):
        print(TTF_GetError())
    color = SDL_Color(180, 189, 180)


    s = "Un Deux Trois Quatre"
    text = b"Un Deux Trois Quatre"
    text2 = bytes(s, "utf-8")

    surface = TTF_RenderText_Solid(font, text2, color)

    x = 50
    y = 30

    srcRect = SDL_Rect(0, 0, surface.contents.w, surface.contents.h)
    dstRect = SDL_Rect(x, y, surface.contents.w, surface.contents.h)

    texture = SDL_CreateTextureFromSurface(graphics.renderer, surface)
    graphics.blit_surface(texture, srcRect, dstRect)


    while(not SDL_QuitRequested()):
        SDL_Delay(250)
        graphics.flip()



    TTF_CloseFont(font)

    TTF_Quit()
    ext.quit()


if __name__ == "__main__":
    main()
