import pygame
import os
import time
from random import shuffle

class MusicPlayer(object):

    def __init__(self, musicdir='music'):
        self.musicdir = musicdir
        self.song_titles = [f for f in os.listdir(musicdir) if f.endswith('.mp3')]
        self.song_paths = [os.path.join(musicdir, st) for st in self.song_titles]
        self.order = range(len(self.song_titles))
        shuffle(self.order)
        self.idx = 0
        self.mixer = pygame.mixer
        self.mixer.init()

    def start_play(self):
        self.mixer.music.load(self.song_paths[self.order[self.idx]])
        self.mixer.music.play()
        print 'Now Playing: {}'.format(self.song_titles[self.order[self.idx]])

    def next_song(self):
        self.mixer.music.stop()
        self.idx += 1
        if self.idx == len(self.song_titles):
            self.idx = 0
            shuffle(self.order)
        self.start_play()

    def fade_pause(self):
        curr_volume = self.mixer.music.get_volume()
        if curr_volume > 0.1:
            curr_volume -= 0.1
            self.mixer.music.set_volume(curr_volume)
            return False
        else:
            self.mixer.music.pause()
            return True

    def resume_pause(self):
        curr_volume = self.mixer.music.get_volume()
        self.mixer.music.unpause()
        while curr_volume <= 1:
            time.sleep(0.2)
            curr_volume += 0.1
            self.mixer.music.set_volume(curr_volume)
        return
