# -*- coding: utf-8 -*-
import os
import time
import random
import re
import math
import codecs
from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import ButtonBehavior, CompoundSelectionBehavior
from kivy.clock import Clock
from kivy.metrics import dp,sp
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.uix.popup import Popup
from random import randint
from functools import partial, singledispatch
from datetime import datetime

from recycleviews import RVPlaylist, RVPlaylistItem
from popups import PopupAddSongToPlaylist, PopupDirChooser, PopupCreatePlaylist, PopupLoadPlaylist
from song import Song
from settings import SettingsScreen
from behaviors import MouseOverBehavior

# icons
# C:\Users\gui\kivy_venv\Lib\site-packages\kivy\tools\theming\defaulttheme

# ffpyplayer
# c:\Users\gui\kivy_venv\Scripts\activate
# python -m pip install ffpyplayer

class FirstScreen(Screen):
    def open_popup_dir_chooser(self):
        app = App.get_running_app()
        popup = PopupDirChooser(path=app.root.ids.settings_screen.browse_dir)
        popup.bind(on_dismiss=self.load_songs_from_dir_popup)
        popup.open()

    def load_songs_from_dir_popup(self, popup=None):
        if popup:
            if popup.closed_by_button == 'select':
                if popup.selection:
                    app = App.get_running_app()
                    app.load_songs_from_dir(popup.selection)

    def open_popup_save_to_playlist(self):
        popup = PopupCreatePlaylist()
        popup.title = "Playlist name (Overwrite)"
        popup.bind(on_dismiss=self.save_to_playlist_by_popup)
        popup.open()

    def save_to_playlist_by_popup(self, popup=None):
        if popup:
            if popup.closed_by_button == 'create':
                if popup.playlist_name:
                    app = App.get_running_app()
                    playlists_dir = app.root.ids.settings_screen.playlists_dir
                    fileabs = os.path.join(playlists_dir, popup.playlist_name + '.playlist')
                    if fileabs:
                        with codecs.open(fileabs, 'w', encoding="utf-8") as playlist_out:
                            for i, song in app.default_playlist:
                                if len(song.file_path.strip()) > 0:
                                    playlist_out.write(song.file_path + '\n')

    def open_popup_load_playlist(self):
        popup = PopupLoadPlaylist()
        popup.open()



        
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class MyScreenManager(ScreenManager):
    pass



class KivyPlayerApp(App):
    default_playlist = []
    played_songs = [] # list of song paths for the 'previous' button
    playing_index = NumericProperty(0)
    selected_index = NumericProperty(0)
    soundLoader = None

    song_secs_elapsed = 0.0
    song_time_elapsed = StringProperty('00:00')
    time_elapsed_formatted = StringProperty('00:00')
    time_tick = 1/20

    volume = NumericProperty(0.01)
    
    bar_width = dp(20)
    playlist_item_height = dp(50)

    last_click = ObjectProperty((-999, 0)) #(index, time.time())

    #on_mouse_over_widgets = ListProperty([])
    #mouse_pos = None

    # storage
    store = None # JsonStore

    def build(self):
        Window.size = (469, 700)
        Window.bind(mouse_pos=self.on_mouse_pos)

        print(os.path.join(os.path.dirname(__file__)))
        Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\firstscreen.kv'))
        Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\popups.kv'))
        Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\settings.kv'))
        Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\recycleviews.kv'))
        Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\buttons.kv'))
        return Builder.load_file(os.path.join(os.path.dirname(__file__), r'kv\kivyplayer.kv'))
        #return MyScreenManager()

    def __init__(self, **kwargs):
        super(KivyPlayerApp, self).__init__(**kwargs)

        print('pwd:', os.getcwd())

        Clock.schedule_once(self.finish_init)
        #Clock.schedule_interval(self.bounce_label, 1/60)
        Clock.schedule_interval(self.song_timer, self.time_tick)
        Clock.schedule_interval(self.update, 1/60)
        #Clock.schedule_interval(self.update, 1)

    def finish_init(self, dt):
        self.store = JsonStore('kivy_settings.json')
        if not self.store.exists('general'):
            self.store.put(
                'general',
                volume=0, 
                browse_dir=os.getcwd(), 
                playlists_dir=os.getcwd(),
                shuffle=False,
                follow=False,
                max_file_size_MB_mb=10)

        self.volume = self.store.get('general')['volume']
        self.root.ids.first_screen.ids.shuffle_button.toggle = self.store.get('general')['shuffle']
        self.root.ids.settings_screen.ids.follow_checkbox.active = self.store.get('general')['follow']

        # binds
        self.root.ids.first_screen.ids.shuffle_button.bind(toggle=self.on_shuffle)
        self.root.ids.settings_screen.ids.follow_checkbox.bind(active=self.on_follow)
        #self.load_songs_from_dir(r"F:\Musicas Game OSTs")

    def check_double_click_song(self, index):
        new_time = time.time()
        new_index = index
        last_index, last_time = self.last_click

        if last_index == new_index and new_time-last_time<=0.2:
            self.last_click = (new_index, new_time)
            self.last_click = (-999, 0)
            self.song_play()
        
        print('last_click:', last_time, 'new_click:', (new_index, new_time), 'delta:', new_time-self.last_click[1])
        self.last_click = (new_index, new_time)
        


    


    def on_mouse_pos(self, window, pos):
        #print(pos)
        #self.mouse_pos = pos
        pass
        
    def update(self, dt):
        app = App.get_running_app()

        # Update bouncing label
        bouncing_label = app.root.ids.first_screen.ids.bouncing_label
        bouncing_label.x -= 1
        if bouncing_label.x < -(bouncing_label.parent.width/2 + bouncing_label.texture_size[0]/2):
            bouncing_label.x = bouncing_label.parent.width/2 + bouncing_label.texture_size[0]/2

        # Do things on MouseOverBehavior widgets
        pos = Window.mouse_pos
        #print(pos)
        try:
            for widget in self.on_mouse_over_widgets:
                local_pos = widget.to_window(*widget.pos)
                if (pos[0] >= local_pos[0] and pos[0] <= local_pos[0]+widget.width
                and pos[1] >= local_pos[1] and pos[1] <= local_pos[1]+widget.height):
                    widget.mouse_over = True
                else:
                    widget.mouse_over = False

        except Exception:
            pass


    def is_shuffle(self):
        return self.root.ids.first_screen.ids.shuffle_button.toggle

    def on_shuffle(self, widget, value):
        # update shuffle settings
        general = self.store.get('general')
        general['shuffle'] = value
        self.store.put('general', **general)

    def is_follow(self):
        return self.root.ids.settings_screen.ids.follow_checkbox.active
        
    def on_follow(self, widget, value):
        app = App.get_running_app()
        general = app.store.get('general')
        general['follow'] = value
        app.store.put('general', **general)

    def song_timer(self, dt):
        #print('dt', dt)
        # Update timer each second
        sl = self.root.ids.first_screen.ids.time_elapsed_slider

        # solves when the load time sums with the elapsed time
        if self.song_secs_elapsed == 0 and dt > self.time_tick*5:
            return

        if self.soundLoader:
            #print(self.soundLoader.state)
            if self.soundLoader.state == "play":
                self.song_secs_elapsed += dt
                sl.value = math.floor(self.song_secs_elapsed) / self.soundLoader.length
                if sl.value>1: sl.value = 1
            else:
                self.song_secs_elapsed = 0
                sl.value = 0
        else:
            self.song_secs_elapsed = 0
            sl.value = 0

        h = math.floor(self.song_secs_elapsed / 3600)
        m = math.floor(self.song_secs_elapsed / 60)
        s = math.floor(self.song_secs_elapsed % 60)
        #print('s', s)
        hs = f"{h:02d}"
        ms = f"{m:02d}"
        ss = f"{s:02d}"
        hms = []
        if h>0: hms.append(hs)
        hms.append(ms)
        hms.append(ss)
        self.song_time_elapsed = ':'.join(hms)
        
        
    def song_play(self):
        if not self.default_playlist:
            return

        rv = self.root.ids.first_screen.ids.rv
        sl = self.root.ids.first_screen.ids.time_elapsed_slider

        index, song = self.default_playlist[self.selected_index]
        # Unload if already playing
        
        # Load selected song file
        self.playing_index = self.selected_index

        if self.soundLoader:
            self.soundLoader.unbind(on_stop=self.on_song_finish)
            self.soundLoader.unload()
        
        try:
            file_size_MB = os.stat(song.file_path).st_size/1024/1024

            print('file_size_MB', file_size_MB)
            if file_size_MB <= 10:
                self.soundLoader = SoundLoader.load(song.file_path)
                self.soundLoader.volume = self.volume

                print('Playing:', 'index:', index, song.file_path)
                self.soundLoader.bind(on_stop=self.on_song_finish)
                
                self.soundLoader.play()
                self.song_secs_elapsed = 0
                sl.value = 0
                # Set playing label
                self.root.ids.first_screen.ids.bouncing_label.text = f"{song.dir_name} - {song.display_name}"
                #sl.max = self.soundLoader.length
                self.played_songs.append(song.file_path)

                if self.is_follow():
                    self.scroll_to_playing()
            else:
                raise Exception(f'ERROR: File bigger than 10MB: {file_size_MB}MB')
        except Exception as e:
            print(str(e))
            Clock.schedule_once(self.song_next, 1)
            
        Clock.schedule_once(partial(rv.highlight_index, self.selected_index))
            

    def on_song_finish(self, *args):
        self.song_next()

        
    def song_next(self, *args):
        if not self.default_playlist:
            return

        if self.is_shuffle():
            self.selected_index = randint(0, len(self.default_playlist)-1)
        else:
            self.selected_index = self.playing_index+1
            if self.selected_index >= len(self.default_playlist)-1:
                self.selected_index = 0
        self.song_play()


    def song_prev(self):
        if not self.is_shuffle():
            if self.playing_index-1 < 0:
                self.selected_index = len(self.default_playlist)-1
            else:
                self.selected_index = self.playing_index-1
            self.song_play()
            return

        if not self.default_playlist:
            return

        if self.is_shuffle():
            print('antes', self.played_songs)
            if len(self.played_songs)>1:
                self.played_songs.pop() # remove last item, which is the same as playing
                print('depois', self.played_songs)
                for index, song in self.default_playlist:
                    if song.file_path == self.played_songs[-1]:
                        self.selected_index = index
                        self.played_songs.pop() # remove because this song will be added again in play
                        self.song_play()
                        break

    def scroll_to_playing(self, *args):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        # scroll only when the items size > the screen size
        if rv.children[0].height < rv.height:
            return

        rv.deselect_all()

        item_size = app.playlist_item_height
        total_items_on_screen = math.floor(rv.height / item_size)
        
        if self.playing_index <= total_items_on_screen:
            rv.scroll_y = 1
        elif self.playing_index > len(self.default_playlist)-total_items_on_screen:
            rv.scroll_y = 0
        else:
            single_item_perc = 1.0/len(self.default_playlist)
            rv.scroll_y = 1 - (single_item_perc * self.playing_index)
            print('single_item_perc', single_item_perc)
        
            #perc = 1-(self.playing_index / len(self.default_playlist))
            #rv.scroll_y = perc #0=fim, 1=inicio

        Clock.schedule_once(partial(rv.highlight_index, self.playing_index))


    def song_stop(self):
        if self.soundLoader:
            self.soundLoader.unbind(on_stop=self.on_song_finish)
            self.soundLoader.stop()
            self.root.ids.first_screen.ids.bouncing_label.text = ""
            self.song_time_elapsed = '00:00'
            self.song_secs_elapsed
        

    def on_volume_value(self, *args):
        value = self.root.ids.first_screen.ids.volume_slider.value
        self.volume = value
        #print(value)
        
        # update volume settings
        general = self.store.get('general')
        general['volume'] = self.volume
        self.store.put('general', **general)
        
        if self.soundLoader:
            self.soundLoader.volume = self.volume
    
    def songs_reload_rv_from_default_playlist(self, dt):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv
        
        i = 0
        for index, song in self.default_playlist:
            rv.data.append({'index': i, 'text': f'{index}. {" - ".join([song.dir_name, song.display_name])}', 'song': song})
            i += 1

        rv.data.append({'index': len(rv.data), 'text': '', 'song': None})

    def song_remove(self, index):
        print('removing:', index)
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        rv.data = []
        #rv.data.pop(index)
        self.default_playlist.pop(index)
        new_default_playlist = []
        scroll_y = rv.scroll_y

        i = 0
        for _, song in self.default_playlist:
            new_default_playlist.append( (i, song) )
            i += 1
        
        self.default_playlist = new_default_playlist

        if self.playing_index == index:
            self.song_stop()

        i = 0
        new_data = []
        for _, song in self.default_playlist:
            new_data.append({'index': i, 'text': f'{i}. {" - ".join([song.dir_name, song.display_name])}', 'song': song})
            i += 1

        #new_data.append({'index': len(new_data), 'text': '', 'song': None})
        rv.data = new_data

        single_item_perc = 1.0/len(self.default_playlist)
        rv.scroll_y = scroll_y + single_item_perc
        
        Clock.schedule_once(partial(rv.highlight_index, index))

    def songs_clear(self):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv
        rv.data = []
        self.default_playlist = []
        self.played_songs = []
        self.playing_index = 0
        self.selected_index = 0
        self.song_stop()


    #def load_from_dir_open_popup(self, dir_path):
    #    popup = PopupDirChooser(self.load_songs_from_dir, path=dir_path)
    #    popup.open()

    def load_songs_from_dir(self, dir_path, append=True):
        print('load_songs_from_dir:', dir_path)
        #print(app.root.ids.first_screen.ids.rv)
        rv = self.root.ids.first_screen.ids.rv

        if not append:
            self.songs_clear()

        # Remove last element, if it's text==''
        if len(rv.data)>0:
            if rv.data[-1]['text'] == '':
                rv.data.pop(-1)

        i = len(rv.data)

        #for subdir, dirs, files in os.walk(r"F:\Musicas Game OSTs"):
        for subdir, dirs, files in os.walk(dir_path):
            for file in files:
                fileabs = os.path.join(subdir, file)
                fname, fext = os.path.splitext(file)
                if fext.lower() == '.mp3':
                    #if n>4:
                    song = Song(fileabs)
                    self.default_playlist.append( (i, song) )
                    rv.data.append({'index': i, 'text': f'{i}. {" - ".join([song.dir_name, song.display_name])}', 'song': song})
                    i += 1
                    #print(fname)
                #if i>30: break
            #if i>30: break
            
        #rv.data = [{'index': index, 'text': f'{index}. {" - ".join([song.dir_name, song.display_name])}', 'song': song} for index, song in self.default_playlist]
        #rv.data.append({'index': len(rv.data), 'text': '', 'song': None})
        
        general = self.store.get('general')
        general['browse_dir'] = dir_path
        self.store.put('general', **general)
        self.root.ids.settings_screen.set_browse_dir(dir_path)

        self.scroll_to_playing()


    def load_songs_from_playlist(self, fileabs, append=True):
        print('load_songs_from_playlist:', fileabs)
        #print(app.root.ids.first_screen.ids.rv)
        rv = self.root.ids.first_screen.ids.rv

        if not append:
            self.songs_clear()

        # Remove last element, if it's text==''
        if len(rv.data)>0:
            if rv.data[-1]['text'] == '':
                rv.data.pop(-1)

        i = len(rv.data)
        #for subdir, dirs, files in os.walk(r"F:\Musicas Game OSTs"):
        with codecs.open(fileabs, 'r', encoding="utf-8") as playlist_in:
            for file in playlist_in:
                if file:
                    fileabs = file.strip()
                    song = Song(fileabs)
                    self.default_playlist.append( (i, song) )
                    rv.data.append({'index': i, 'text': f'{i}. {" - ".join([song.dir_name, song.display_name])}', 'song': song})
                    i += 1

        #rv.data = [{'index': index, 'text': f'{index}. {" - ".join([song.dir_name, song.display_name])}', 'song': song} for index, song in self.default_playlist]
        #rv.data.append({'index': len(rv.data), 'text': '', 'song': None})
        
        self.scroll_to_playing()


    def goto_settings_screen(self):
        self.root.current = 'settings'
    
    def goto_first_screen(self):
        self.root.current = 'first'

if __name__ == '__main__':
    # run loop
    KivyPlayerApp().run()
