

from sdl2 import *
from sdl2.sdlttf import *

from graphics import Graphics


class FontManager(object):
    __fonts = {}

    @staticmethod
    def __get_surface(fontname, size, color, text):
        if not TTF_WasInit():
            TTF_Init()
        if (fontname not in FontManager.__fonts or
                size not in FontManager.__fonts[fontname]):
            raise Exception("Size %d for font %s is not loaded." %
                            (size, fontname))
        used_font = FontManager.__fonts[fontname][size]
        if isinstance(color, SDL_Color):
            used_color = color
        else:
            used_color = SDL_Color(color[0], color[1], color[2])
        text = bytes(text, "utf-8")
        surface = TTF_RenderUTF8_Blended(used_font, text, used_color)
        return surface

    @staticmethod
    def draw_text(graphics, fontname, size, color, text, x, y):
        """Render text with the specified font, size and color and blit it at
        the coordinates (x, y).
        `fontname` is the name which was specified when the font was loaded.
        `color` is a 3-uple of numbers in the range [0, 255].
        """
        surface = FontManager.__get_surface(fontname, size, color, text)
        w, h = surface.contents.w, surface.contents.h
        src_rect = SDL_Rect(0, 0, w, h)
        dst_rect = SDL_Rect(round(x), round(y), w, h)
        texture = SDL_CreateTextureFromSurface(graphics.renderer, surface)
        graphics.blit_surface(texture, src_rect, dst_rect)
        SDL_DestroyTexture(texture)
        SDL_FreeSurface(surface)

    @staticmethod
    def draw_text_centered(graphics, fontname, size, color, text, x, y):
        """Render text with the specified font, size and color and blit it
        centered at the coordinates (x, y).
        `fontname` is the name which was specified when the font was loaded.
        `color` is a 3-uple of numbers in the range [0, 255].
        """
        surface = FontManager.__get_surface(fontname, size, color, text)
        w, h = surface.contents.w, surface.contents.h
        src_rect = SDL_Rect(0, 0, w, h)
        dst_rect = SDL_Rect(round(x - w / 2), round(y - h / 2), w, h)
        texture = SDL_CreateTextureFromSurface(graphics.renderer, surface)
        graphics.blit_surface(texture, src_rect, dst_rect)
        SDL_DestroyTexture(texture)
        SDL_FreeSurface(surface)

    @staticmethod
    def load_font(path, name, size):
        """Load a font to be used later.
        path : str, path to the .ttf file
        name : str, name that will be used to retrieve the font later
        size : int, size of the font
        Exemple :
            FontManager.load_font("resources/Free-Helvetica.ttf", "helvetica", 14)
        """
        if not TTF_WasInit():
            TTF_Init()
        if (not name in FontManager.__fonts or
                not size in FontManager.__fonts[name]):
            path = bytes(path, "utf-8")
            font = TTF_OpenFont(path, size)
            if not font:
                raise Exception("sdl_TTF error : %s" % TTF_GetError().decode())
            FontManager.__fonts[name] = FontManager.__fonts.get(name, {})
            FontManager.__fonts[name][size] = font

    @staticmethod
    def print_available_fonts():
        for f in FontManager.__fonts:
            print(f)
            for size in FontManager.__fonts[f]:
                print("   ", size)
