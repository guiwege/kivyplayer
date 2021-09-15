

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior, CompoundSelectionBehavior
from behaviors import MouseOverBehavior


class ButtonLabel(ButtonBehavior, MouseOverBehavior, Label):
    pass

class ButtonImage(ButtonBehavior, MouseOverBehavior, Image):
    pass

class ButtonLabelAddSongToPlaylist(ButtonLabel):
    def unset_color(self, *args):
        #super(ButtonLabelAddSongToPlaylist, self).unset_color()
        #app = App.get_running_app()
        #rv = app.root.ids.first_screen.ids.rv
        #Clock.schedule_once(partial(rv.highlight_index, self.parent.index))
        pass
        
class ButtonLabelShuffle(ButtonBehavior, Label):
    pass

class ButtonLabelToggle(ButtonBehavior, MouseOverBehavior, Label):
    toggle = BooleanProperty(False)

    def on_release(self, *args):
        self.toggle = not self.toggle
        print(self.toggle)


class ButtonImageToggle(ButtonBehavior, MouseOverBehavior, Image):
    toggle = BooleanProperty(False)

    def on_release(self, *args):
        self.toggle = not self.toggle
        print(self.toggle)


class ButtonAsyncImage(ButtonBehavior, MouseOverBehavior, AsyncImage):
    pass