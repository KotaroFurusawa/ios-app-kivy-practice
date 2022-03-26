from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from workoutbanner import WorkoutBanner
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
        api_url = self.secret['FIREBASE']['R_DB']['URL']
        result = requests.get(f"{api_url}{self.my_friend_id}.json")
        data = json.loads(result.content.decode())

        # streakラベルをDBのdataから設定
        streak_label = self.root.ids["home_screen"].ids["streak_label"]
        streak_label.text = str(data['streak']) + " Day Streak!"

        # プロフィール画像をDBのdataから設定
        avatar_image = self.root.ids["avatar_image"]
        avatar_image.source = "icons/avatars/" + data["avatar"]

        # 人気のトレーニングをホームスクリーンに表示
        banner_grid = self.root.ids["home_screen"].ids["banner_grid"]
        workouts = data["workouts"][1:]
        for workout in workouts:
            print(workout["workout_img"])
            print(workout["description"])
            w = WorkoutBanner(
                workout_img=workout["workout_img"],
                description=workout["description"],
                type_image=workout["type_image"],
                number=workout["number"],
                units=workout["units"],
                likes=workout["likes"])
            banner_grid.add_widget(w)

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        # rootはmain.kvのGridLayout(rootウィジェット)のこと
        screen_manager.current = screen_name
        # 現在のスクリーンを変更する


MainApp().run()
