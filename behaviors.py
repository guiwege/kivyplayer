
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.behaviors.button import ButtonBehavior
from time import time

class MouseOverBehavior(object):
    mouse_over = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(MouseOverBehavior, self).__init__(**kwargs)
        app = App.get_running_app()
        if not hasattr(app, 'mouse_over_behavior_widgets'):
            app.mouse_over_behavior_widgets = []
        app.mouse_over_behavior_widgets.append(self)

class DoubleClickBehavior(ButtonBehavior):
    prev_click_epoch = 0

    def __init__(self, **kwargs):
        super(DoubleClickBehavior, self).__init__(**kwargs)
        app = App.get_running_app()
        if not hasattr(app, 'double_click_behavior_widgets'):
            app.double_click_behavior_widgets = []
        app.double_click_behavior_widgets.append(self)

    def on_release(self):
        new_click_epoch = time()
        if new_click_epoch-self.prev_click_epoch <= 0.2:
            self.double_click()

        self.prev_click_epoch = new_click_epoch

    def double_click(self):
        print('double clicked')

