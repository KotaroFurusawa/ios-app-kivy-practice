from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


GUI = Builder.load_file("main.kv")


class MainApp(App):
    def build(self):
        return GUI

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screem_manager"]
        # rootはmain.kvのGridLayout(rootウィジェット)のこと
        screen_manager.current = screen_name
        # 現在のスクリーンを変更する


MainApp().run()