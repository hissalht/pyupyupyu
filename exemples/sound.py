from sdl2 import *
from sdl2.sdlmixer import *
import sdl2.ext as ext


def main():
    ext.init()

    #Initialiser l'audio
    Mix_OpenAudio(22050, AUDIO_S16SYS, 2, 1024)

    #Creation de 16 canaux
    #Chaque son doit etre joué sur un canal
    #Avec 16 canaus on peut jouer 16 sons simultanement
    Mix_AllocateChannels(16)

    #charger le sample
    chunk = Mix_LoadWAV(b"quack.wav")

    #jouer le son, on récupere le canal dans lequel le son est joué
    # Mix_PlayChannel(canal, sample, loop)
    # canal : le canal dans lequel on joue le son, -1 = n'importe lequel de libre
    # loop : 0 = joué 1 fois, 2 = joué 3 fois, -1 = joué à l'infini
    channel = Mix_PlayChannel(-1, chunk, -1)

    #Attendre tant que le son est joué
    while(Mix_Playing(channel)):
        SDL_Delay(250)

    #décharger le sample
    Mix_FreeChunk(chunk)

    ext.quit()

if __name__ == "__main__":
    main()
