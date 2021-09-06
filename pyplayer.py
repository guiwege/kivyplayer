#import pygame
#import multiprocessing
#from threading import Thread
#import playsound
import os
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from random import randint


songs = set()
for subdir, dirs, files in os.walk(r"F:\Musicas Game OSTs"):
    for file in files:
        fileabs = os.path.join(subdir, file)
        fname, fext = os.path.splitext(file)

        if fext.lower() == '.mp3':
            songs.add(fileabs)

songs = list(songs)

print(songs)



while False:
    i = randint(0, len(songs))
    
    song = songs[i]
    print(song)
    playsound.playsound(song, True)
    #p = multiprocessing.Process(target=playsound.playsound, args=(song,))
    #p.start()
    #m = Thread(target=playsound.playsound,args=[songs[i]])
    #m.start()

    input("press ENTER to next")
    #p.terminate()
    

class MusicWindow(App):
 
    def build(self):
        
        #load the mp3 music 
        music = SoundLoader.load('F:\\Musicas Game OSTs\\Muramasa\\Oboro Muramasa OST #34.mp3')
 
        #check the exisitence of the music 
        if music:
            music.play()
 
        return Label(text = "Music is playing")
 
 
if __name__ == "__main__":
    window = MusicWindow()
    window.run()

