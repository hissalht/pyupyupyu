
from sdl2 import *
from sdl2.sdlmixer import *
import sdl2.ext as ext


class AudioManager:
    """Used to load and play musics and sounds."""
    __musics = {}
    __sounds = {}

    @staticmethod
    def init_audio():
        """Must be called before using other static methods.
        Initialize the audio channels.
        """
        Mix_OpenAudio(22050, AUDIO_S16SYS, 2, 1024)
        Mix_AllocateChannels(64)

    @staticmethod
    def load_sound(path, name):
        """Load the sound file located at `path` and store it under the passed
        name. The recommended file format is `.WAV`.
        Once the sound is loaded. It can be played by calling
        AudioManager.play_sound(name).
        """
        if name in AudioManager.__sounds:
            raise Exception("A sound with this name is already loaded.")
        chunk = Mix_LoadWAV(bytes(path, "utf-8"))
        if not chunk:
            raise FileNotFoundError("Impossible to load %s" % name)
        if chunk in AudioManager.__sounds.values():
            raise Exception("That sound is already loaded.")
        AudioManager.__sounds[name] = chunk

    @staticmethod
    def unload_sound(name):
        """Unload the sound stored under `name` when it is not needed
        anymore."""
        if name not in AudioManager.__sounds:
            raise Exception("that sound is not loaded.")
        chunk = AudioManager.__sounds[name]
        Mix_FreeChunk(chunk)
        del AudioManager.__sounds[name]

    @staticmethod
    def play_sound(name):
        """Play the sound stored under `name`."""
        if name not in AudioManager.__sounds:
            raise Exception("that sound is not loaded.")
        Mix_PlayChannel(-1, AudioManager.__sounds[name], 0)

    @staticmethod
    def load_music(path, name):
        """Load the music file located at `path` and store it under the passed
        name. The recommended file format is `.OGG`.
        Once the music is loaded. It can be played by calling
        AudioManager.play_music(name).
        """
        if name in AudioManager.__musics:
            raise Exception("A music with this name is already loaded.")
        music = Mix_LoadMUS(bytes(path, "utf-8"))
        if not music:
            raise FileNotFoundError("Impossible to load %s" % name)
        if music in AudioManager.__musics.values():
            raise Exception("That music is already loaded.")
        AudioManager.__musics[name] = music

    @staticmethod
    def unload_music(name):
        """Unload the music stored under `name` when it is not needed
        anymore."""
        if name not in __music:
            raise exception("that music is not loaded.")
        music = AudioManager.__music[name]
        Mix_FreeMusic(music)
        del AudioManager.__music[name]

    @staticmethod
    def play_music(name, loop=False):
        """Play the music stored under `name`. If `loop` is True, the music
        will be looped until it is manually stopped."""
        if name not in AudioManager.__musics:
            raise exception("that music is not loaded.")
        if loop:
            Mix_PlayMusic(AudioManager.__musics[name], -1)
        else:
            Mix_PlayMusic(AudioManager.__musics[name], 1)

    @staticmethod
    def pause_music():
        """Pause the currently playing music."""
        Mix_PauseMusic()

    @staticmethod
    def resume_music():
        """Resume playing the current music."""
        Mix_ResumeMusic()

    @staticmethod
    def set_music_volume(vol):
        vol *= 128
        vol = int(vol)
        Mix_VolumeMusic(vol)

def load_audio():
    AudioManager.load_music("ressources/music/cena.ogg", "cena")
    AudioManager.load_music("ressources/music/theme.ogg", "theme")
    AudioManager.load_sound("ressources/music/pyu.wav", "laser")
    AudioManager.load_sound("ressources/music/explosion.wav", "explosion")
    AudioManager.load_sound("ressources/music/explosion2.wav", "explosion2")
    AudioManager.load_sound("ressources/music/bleep.wav", "bleep")
    AudioManager.load_sound("ressources/music/powerup.wav", "powerup")