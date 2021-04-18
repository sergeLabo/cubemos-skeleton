## sound.py

#############################################################################
# Copyright (C) SergeBlender April 2013
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franproplin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#############################################################################

"""
Class générique qui permet de gérer facilement le son

gl est le GameLogic, get with : from bge import logic as gl

Appel de cette classe où tous les sons sont dans une liste avec :
    import aud
    soundList = ["boum", ...] avec les fichiers boum.ogg etc...
    Création de l'objet qui est un dictionnaire
        gl.sound = EasyAudio(soundList)
        soit { "boum": fabrique de boum.ogg, ....}
    Joue le son boum
        gl.sound["boum"].play()
    Stop le son
        gl.sound["boum"].stop()
    Idem repeat, pause
"""

from time import sleep
from bge import logic as gl
import aud


class Factory():
    def __init__(self, audio_file_path, buffered=True):
        ''' audio_file_path = "//audio/comment/boum.ogg"
            buffered = Boolean '''
        self.device = aud.device()
        # Dictionnaire des fichiers son
        self.sound = gl.expandPath(audio_file_path)

        # Buffer par défaut
        self.buffered = buffered
        # load sound file
        try:
            self.factory = aud.Factory(self.sound)
        except:
            print("Pas de fichier son :", self.sound)
        if self.buffered:
            try:
                self.factory_buffered = aud.Factory.buffer(self.factory)
            except:
                print("Pas de fichier son :", self.sound)

    def set_volume(self, vol):
        if not self.buffered:
            self.handle.volume = vol
        if self.buffered:
            self.handle_buffered.volume = vol

    def set_pitch(self, pitch):
        if not self.buffered:
            self.handle.pitch = pitch
        if self.buffered:
            self.handle_buffered.pitch = pitch

    def play(self, volume=1):
        # play the audio, this return a handle to control play/pause/stop
        if not self.buffered:
            self.handle = self.device.play(self.factory)
            self.handle.volume = volume
        if self.buffered:
            self.handle_buffered = self.device.play(self.factory_buffered)
            self.handle_buffered.volume = volume

    def repeat(self, volume=1):
        if not self.buffered:
            self.handle = self.device.play(self.factory)
            self.handle.loop_count = -1
            self.handle.volume = volume
        if self.buffered:
            self.handle_buffered = self.device.play(self.factory_buffered)
            self.handle_buffered.loop_count = -1
            self.handle_buffered.volume = volume

    def pause(self):
        if not self.buffered:
            self.handle.pause()
        if self.buffered:
            self.handle_buffered.pause()

    def stop(self):
        if not self.buffered:
            self.handle.stop()
        if self.buffered:
            self.handle_buffered.stop()


class EasyAudio(dict):
    def __init__(self, soundList, path, buffered=True):
        ''' soundList = ["boum", ...]
            path example "//audio/comment/" '''
        for s in soundList:
            audio_file_path = path + s + ".ogg"
            self[s] = Factory(audio_file_path, buffered)
