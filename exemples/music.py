
from sdl2 import *
from sdl2.sdlmixer import *
import sdl2.ext as ext


def main():
    ext.init()

    # initialisation de la sortie audio
    Mix_OpenAudio(22050, AUDIO_S16SYS, 2, 1024)

    # chargement de la musique
    music = Mix_LoadMUS(b"dead.ogg")

    # On joue la musique
    Mix_PlayMusic(music, -1)

    # On attend 8 secondes
    SDL_Delay(8000)

    # On va directement à la 60eme seconde
    Mix_SetMusicPosition(60.0)

    SDL_Delay(5000)

    # On met la musique en pause
    Mix_PauseMusic()

    SDL_Delay(1000)

    # on reprend la lecture
    Mix_ResumeMusic()

    SDL_Delay(5000)

    # On revient au début de la musique
    Mix_RewindMusic()

    while(not SDL_QuitRequested()):
        SDL_Delay(250)


    # décharger la musique
    Mix_FreeMusic(music)
    ext.quit()

if __name__ == "__main__":
    main()
