
import random
import os
import codecs
from kivy.clock import Clock
from kivy.app import App
from kivy.event import ObjectWithUid
from kivy.uix.recycleview import RecycleView, RecycleViewBehavior
from kivy.uix.popup import Popup
from kivy.metrics import dp,sp
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ObjectProperty
from behaviors import MouseOverBehavior
from buttons import ButtonLabel
from functools import partial

class PopupAddSongToPlaylist(Popup):
    song_name = StringProperty('')
    
    def __init__(self, song, **kwargs):
        #self.kwargs = kwargs
        #self.song = self.kwargs['song']
        self.song = song
        self.song_name = self.song.dir_name + ' - ' + self.song.display_name
        super(PopupAddSongToPlaylist, self).__init__()
        Clock.schedule_once(self.finish_init)

    def finish_init(self, dt):
        self.show_playlists()
        
    def show_playlists(self):
        app = App.get_running_app()
        playlists_dir = app.root.ids.settings_screen.playlists_dir
        self.ids.sv.children[0].clear_widgets()
        print('loading playlists at playlists_dir:', playlists_dir)
        try:
            for file in os.listdir(playlists_dir):
                if os.path.isfile(file):
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    if ext=='.playlist':
                        item = PopupAddSongToPlaylistItem(file, self.song)
                        self.ids.sv.children[0].add_widget(item)
        except Exception as e:
            pass
        
    def open_create_empty_playlist_popup(self):
        popup = PopupCreatePlaylist()
        popup.bind(on_dismiss=self.create_empty_playlist_by_popup)
        popup.open()

    def create_empty_playlist_by_popup(self, popup=None):
        print('popup:', popup, 'closed_by_button:', popup.closed_by_button, 'playlist_name:', popup.playlist_name)
        if popup:
            if popup.closed_by_button == 'create':
                if popup.playlist_name:
                    app = App.get_running_app()
                    playlists_dir = app.root.ids.settings_screen.playlists_dir
                    fileabs = os.path.join(playlists_dir, popup.playlist_name + '.playlist')
                    if fileabs:
                        with codecs.open(fileabs, 'w',  encoding="utf-8") as new_file:
                            pass
                        self.show_playlists()
                        
class PopupAddSongToPlaylistRV(RecycleView):
    pass

class PopupAddSongToPlaylistItem(BoxLayout, MouseOverBehavior):
    playlist_name = StringProperty('')
    song_count = NumericProperty(0)
    songs_total = NumericProperty(0)
    song = ObjectProperty(None)
    working = BooleanProperty(False)

    def __init__(self, playlist_path, song, **kwargs):
        super(PopupAddSongToPlaylistItem, self).__init__(**kwargs)
        self.playlist_path = playlist_path
        self.song = song
        self.playlist_basename = os.path.basename(playlist_path)
        self.playlist_name, _ = os.path.splitext(self.playlist_basename)
        self.playlist_name = self.playlist_name.title()

        with codecs.open(self.playlist_path, 'r', encoding="utf-8") as playlist_in:
            for line in playlist_in:
                self.songs_total += 1
                if line.strip() == song.file_path.strip():
                    self.song_count += 1

        #self.song_count = 0
        Clock.schedule_once(self.finish_init)

    def finish_init(self, dt):
        print(self.parent)

    def playlist_add(self):
        if self.working: return

        self.working = True
        playlist_files = []
        with codecs.open(self.playlist_path, 'r', encoding="utf-8") as playlist_in:
            for file in playlist_in:
                playlist_files.append(file.strip())
                
        playlist_files.append(self.song.file_path)

        with codecs.open(self.playlist_path, 'w', encoding="utf-8") as playlist_out:
            for file in playlist_files:
                if len(file.strip()) > 0:
                    playlist_out.write(file + '\n')
        
        self.song_count += 1
        self.working = False

    def playlist_remove(self):
        if self.working: return

        self.working = True
        playlist_files = []
        with codecs.open(self.playlist_path, 'r', encoding="utf-8") as playlist_in:
            for file in playlist_in:
                playlist_files.append(file.strip())

        try:
            playlist_files.remove(self.song.file_path)

            with codecs.open(self.playlist_path, 'w', encoding="utf-8") as playlist_out:
                for file in playlist_files:
                    if len(file.strip()) > 0:
                        playlist_out.write(file + '\n')

            self.song_count -= 1
        except ValueError as e:
            print('song:', '\"self.song.file_path\"', 'not in ', '\"self.playlist_path\"')
        self.working = False


class PopupLoadPlaylist(Popup):
    def __init__(self, **kwargs):
        super(PopupLoadPlaylist, self).__init__(**kwargs)
        Clock.schedule_once(self.finish_init)

    def finish_init(self, dt):
        self.show_playlists()
        pass
        
    def show_playlists(self):
        app = App.get_running_app()
        playlists_dir = app.root.ids.settings_screen.playlists_dir
        self.ids.sv.children[0].clear_widgets()
        print('loading playlists at playlists_dir:', playlists_dir)
        for file in os.listdir(playlists_dir):
            fileabs = os.path.join(app.root.ids.settings_screen.playlists_dir, file)
            if os.path.isfile(file):
                fname, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext=='.playlist':
                    #print(fname)
                    item = ButtonLabel(text=fname, size_hint=(1, None), height=dp(50))
                    item.bind(on_release=partial(app.load_songs_from_playlist, fileabs))
                    item.bind(on_release=self.dismiss)
                    self.ids.sv.children[0].add_widget(item)

class PopupDirChooser(Popup):
    selection = ''
    title = StringProperty('')
    path = StringProperty('')
    closed_by_button = StringProperty('') 
    #agora
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(PopupDirChooser, self).__init__()
        #self.selection = self.kwargs['path']
        self.path = self.kwargs['path']
        self.title = self.path
        self.selection = self.path
        
    def finish_init(self, dt):
        self.ids.fc.title = self.ids.fc.path

    def on_selection(self, *args):
        print('selection:', 'args:', args)
        fc = self.ids.fc
        #self.selection = fc.selection and fc.selection[0] or ''
        self.selection = fc.selection[0] if hasattr(fc, 'selection') and len(fc.selection)>0 else ''
        self.title = self.selection

    def select(self):
        self.closed_by_button = 'select'
        super(PopupDirChooser, self).dismiss()

class PopupCreatePlaylist(Popup):
    playlist_name = StringProperty('')
    closed_by_button = StringProperty('')
    
    def __init__(self, **kwargs):
        #self.kwargs = kwargs
        super(PopupCreatePlaylist, self).__init__()
    
    def set_playlist_name(self, *args):
        #print('self:', self, 'args:', args, 'playlist_name:', self.playlist_name)
        #self.playlist_name = value
        pass

    def cancel(self):
        super(PopupCreatePlaylist, self).dismiss()

    def create(self):
        self.closed_by_button = 'create'
        super(PopupCreatePlaylist, self).dismiss()
        return
        app = App.get_running_app()
        playlist_name = self.ids.input_playlist_name.text + '.playlist'
        playlists_dir = app.root.ids.settings_screen.playlists_dir
        fileabs = os.path.join(playlists_dir, playlist_name)

        try:
            #self.kwargs['do_before_dismiss_callback']()
            self.do_before_dismiss_callback(fileabs)
        except Exception as e:
            pass
        super(PopupCreatePlaylist, self).dismiss()
