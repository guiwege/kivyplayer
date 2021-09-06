

from kivy.app import App
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior, CompoundSelectionBehavior
from behaviors import MouseOverBehavior


class ButtonLabel(ButtonBehavior, MouseOverBehavior, Label):
    def __init__(self, **kwargs):
        super(ButtonLabel, self).__init__(**kwargs)
        
        self.normal_color = (1, 1, 1, 1)
        self.toggle_color = (0, 1, 1, 1)

    def on_press(self):
        return
        self.color = self.toggle_color
        Clock.schedule_once(self.unset_color, 0.1)
        pass

    def unset_color(self, *args):
        return
        self.color = self.normal_color
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

