

import os
import time
import random
import re
import math
from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
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
from random import randint
from functools import partial, singledispatch
from datetime import datetime
from recycleviews import RVPlaylist, RVPlaylistItem
from popups import PopupAddSongToPlaylist, PopupDirChooser
from song import Song


class SettingsScreen(Screen):
    playlists_dir = StringProperty('')
    browse_dir = StringProperty('')

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.finish_init)

    def finish_init(self, dt):
        app = App.get_running_app()
        self.playlists_dir = app.store.get('general')['playlists_dir']
        self.browse_dir = app.store.get('general')['browse_dir']

    def set_playlists_dir(self, value):
        app = App.get_running_app()

        general = app.store.get('general')
        general['playlists_dir'] = value
        app.store.put('general', **general)

        self.playlists_dir = value

    def set_playlists_dir_by_popup(self, popup=None):
        if popup:
            if popup.closed_by_button:
                self.set_playlists_dir(popup.selection)
        
    def set_browse_dir(self, value):
        app = App.get_running_app()

        general = app.store.get('general')
        general['browse_dir'] = value
        app.store.put('general', **general)

        self.browse_dir = value


    def open_popup_dir_chooser(self):
        popup = PopupDirChooser(path=self.playlists_dir)
        popup.bind(on_dismiss=self.set_playlists_dir_by_popup)
        popup.open()