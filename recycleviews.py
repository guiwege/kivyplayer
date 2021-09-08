
import os
import time
import random
import re
import math
from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import ButtonBehavior, CompoundSelectionBehavior, DragBehavior
from kivy.clock import Clock
from kivy.metrics import dp,sp
from kivy.graphics import Color
from kivy.core.window import Window
from random import randint
from functools import partial
from datetime import datetime
from popups import PopupAddSongToPlaylist
from behaviors import MouseOverBehavior


class RVPlaylist(RecycleView):

    def __init__(self, **kwargs):
        super(RVPlaylist, self).__init__(**kwargs)
        self.bind(on_scroll_y=self.on_scroll_y)

    def on_scroll_y(self, *args):
        #print(self.scroll_y)
        pass

    def highlight_index(self, index, *args):
        print('highlight_index:', index)
        self.deselect_all()

        app = App.get_running_app()
        controller = app.root.ids.first_screen.ids.rv.ids.controller

        for node in controller.children:
            if node.index == index:
                controller.select_node(node)
                controller.selected_nodes = [index]
                controller.apply_selection(node.index, node, True)
                break



    def deselect_all(self):
        print('deselect_all')
        # deselect all
        app = App.get_running_app()
        controller = app.root.ids.first_screen.ids.rv.ids.controller
        controller.selected_nodes = []
        
        for node in controller.children:
            controller.deselect_node(node)
            controller.apply_selection(node.index, node, False)









class RVPlaylistItemNew(RecycleDataViewBehavior, MouseOverBehavior, RelativeLayout):
    ''' Add selection support to the Label '''
    index = NumericProperty(0)
    selected = BooleanProperty(True)
    selectable = BooleanProperty(True)
    text = StringProperty('')
    song = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(RVPlaylistItemNew, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        ''' Add selection on touch down '''
        if super(RVPlaylistItemNew, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            print('on_touch_down:', touch)
            
            rv.deselect_all()
            return self.parent.select_with_touch(self.index, touch)

    def on_touch_up(self, touch):
        #print(self.y)
        pass
        
    def apply_selection(self, rv, index, is_selected):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        self.selected = is_selected
        if is_selected:
            print("selection changed to {0} :{1}".format(index, rv.data[index]))
            app = App.get_running_app()
            app.selected_index = self.index
        else:
            pass
        
    def open_popup_add_song_to_playlist(self):
        popup = PopupAddSongToPlaylist(song=self.song)
        popup.bind(on_dismiss=partial(print, 1))
        popup.bind(on_dismiss=partial(print, 2))
        popup.open()










class RVPlaylistItem(RecycleDataViewBehavior, RelativeLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #with self.canvas.before:
        #    Color(1, 0, .4, mode='rgb')
        #self.last_item = kwargs.get('last_item')
        #Clock.schedule_once(self.finish_init)


    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(RVPlaylistItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        ''' Add selection on touch down '''
        if super(RVPlaylistItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            print('on_touch_down:', touch)
            
            rv.deselect_all()
            return self.parent.select_with_touch(self.index, touch)

    def on_touch_up(self, touch):
        #print(self.y)
        pass
        
    def apply_selection(self, rv, index, is_selected):
        app = App.get_running_app()
        rv = app.root.ids.first_screen.ids.rv

        self.selected = is_selected
        if is_selected:
            print("selection changed to {0} :{1}".format(index, rv.data[index]))
            #print('apply_selection self:', self)
            app = App.get_running_app()
            app.selected_index = self.index
        else:
            #print("selection removed for {0}".format(rv.data[index]))
            pass
        
    def open_popup_add_song_to_playlist(self):
        popup = PopupAddSongToPlaylist(song=self.song)
        popup.bind(on_dismiss=partial(print, 1))
        popup.bind(on_dismiss=partial(print, 2))
        popup.open()



