from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileChooserListView


class SrcChooser(RelativeLayout):
    pass


class DstChooser(RelativeLayout):
    pass


class Folder_Syncer(Widget):
    fc_src = ObjectProperty(None)
    fc_dst = ObjectProperty(None)
    sync_btn = ObjectProperty(None)
    add_btn = ObjectProperty(None)


class Folder_SyncerApp(App):
    def build(self):
        app = Folder_Syncer()
        return app


if __name__ == '__main__':
    Folder_SyncerApp().run()
