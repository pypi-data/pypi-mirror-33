"""
The Audio module contains a few simple functions and a class used to control sound playback in the engine.

When registering a soundclip, the file should be loaded as an instance of the Sound class from this module.

Music and standard sounds should be played differently however. It is advisable for music to be played using the functions in this module, in order to prevent Pygame from cutting it off during channel allocation.

However normal sounds should be played using the play method of the Sound class. This allows Pygame to optimise the channel selection and minimise sound interruptions.
"""

import pygame

try:
    # Reserve the first channel to ensure automatic channel allocation doesn't break the music
    pygame.mixer.set_reserved(1)
    MUSIC_CHANNEL = pygame.mixer.Channel(0)
    ALL_CHANNELS = [pygame.mixer.Channel(a) for a in range(1, 8)]
except pygame.error:
    print('[WARNING] pygame.init() has not yet been called. The sound system is not going to work.')
musicPaused = False

class Sound(pygame.mixer.Sound):
    """
    A subclass of pygame.mixer.Sound, used for storing sound objects in the M.A.T.A engine.

    This class offers all of the same methods as the Pygame Sound class, with an additional filename field for ease-of-access. See https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound for details.

    All sounds should be stored as an instance of this object, music or not.
    """
    def __init__(self, filename):
        if not isinstance(filename, str):
            raise TypeError('Sound class parameter must be a filename, not \'{}\''.format(filename.__class__.__name__))

        # Set the filename field, then call the superclass
        #: The filename of the audio file, with the prepended path and file extension stripped off
        self.filename = filename.split('/')[-1].split('.')[-2]
        super().__init__(filename)

    def getFilename(self):
        """
        Get the filename of the Sound object.

        :returns: Filename as a string, or None
        """
        return self.filename

def playMusic(soundObj=None, loops=0, maxtime=0, fade_ms=0):
    """
    Play ``soundObj`` as music.

    ``loops`` is the number of times to repeat ``soundObj`` after the first time. E.g. if it is 3, ``soundObj`` will be played 4 times (the first time, then three more).

    If ``loops`` is -1 then ``soundObj`` will repeat indefinitely.

    ``maxtime`` stops playback of ``soundObj`` after a given number of milliseconds.

    ``fade_ms`` is the number of milliseconds over which to fade ``soundObj`` in.
    """
    global musicPaused

    # Check if a sound is paused, or that no new sound was given to be played
    if soundObj is None or musicPaused:
        musicPaused = False
        MUSIC_CHANNEL.unpause()
        return

    MUSIC_CHANNEL.play(soundObj, loops, maxtime, fade_ms)

def stopMusic(fadeout=0):
    """
    Stop any currently playing music.

    If ``fadeout`` is specified, the music will stop after fading out over ``fadeout`` milliseconds.

    Music stopped this way must be restarted using the ``playMusic`` function.
    """
    if not fadeout:
        MUSIC_CHANNEL.stop()
    else:
        MUSIC_CHANNEL.fadeout(fadeout)

def pauseMusic():
    """
    Pause the currently playing music.

    Music can be resumed by calling ``playMusic()``.
    """
    MUSIC_CHANNEL.pause()
    musicPaused = True

def setMusicVolume(level):
    """
    Set the volume level of music to ``level``.

    :returns: True if successful, False if an error occurred.
    """
    if not (0 <= level <= 1):
        print('[WARNING] Invalid volume for music.')
        return False

    MUSIC_CHANNEL.set_volume(level)
    return True

def setFXVolume(level):
    """
    Set the volume level of all non-music sounds to ``level``.

    :returns: True if successful, False if an error occurred.
    """
    if not (0 <= level <= 1):
        print('[WARNING] Invalid volume for sound.')
        return False

    # Iterate and set the sound levels
    for c in range(len(ALL_CHANNELS)):
        ALL_CHANNELS[c].set_volume(level)
    return True
