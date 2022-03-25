from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
import requests
import json


class HomeScreen(Screen):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class SettingsScreen(Screen):
    pass


GUI = Builder.load_file("main.kv")


class MainApp(App):
    my_friend_id = 1
    secret = json.load(open('./settings/secret_setting.json', 'r'))['SECRET']

    def build(self):
        return GUI

    def on_start(self):
        # dbからデータ取得
        # 人気のトレーニングをホームスクリーンに表示
        api_url = self.secret['FIREBASE']['R_DB']['URL']
        result = requests.get(f"{api_url}{self.my_friend_id}.json")
        data = json.loads(result.content.decode())

        # streakラベルをDBのdataから設定
        streak_label = self.root.ids["home_screen"].ids["streak_label"]
        streak_label.text = str(data['streak']) + " Day Streak!"

        # プロフィール画像をDBのdataから設定
        avatar_image = self.root.ids["home_screen"].ids["avatar_image"]
        avatar_image.source = "icons/avatars/" + data["avatar"]

        workouts = data["workouts"][1:]
        for workout in workouts:
            print(workout["workout_img"])
            print(workout["units"])

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        # rootはmain.kvのGridLayout(rootウィジェット)のこと
        screen_manager.current = screen_name
        # 現在のスクリーンを変更する


MainApp().run()
