
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.app import App

class MouseOverBehavior(object):
    mouse_over = BooleanProperty(False)
    parent_scrollview = None

    def __init__(self, **kwargs):
        super(MouseOverBehavior, self).__init__(**kwargs)
        app = App.get_running_app()
        if not hasattr(app, 'on_mouse_over_widgets'):
            app.on_mouse_over_widgets = []
        app.on_mouse_over_widgets.append(self)

