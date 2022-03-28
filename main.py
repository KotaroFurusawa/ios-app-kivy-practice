from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from workoutbanner import WorkoutBanner
from functools import partial
from os import walk
from myfirebase import MyFirebase
import requests
import json


class HomeScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ChangeAvatarScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class LabelButton(ButtonBehavior, Label):
    pass


GUI = Builder.load_file("main.kv")


class MainApp(App):
    my_friend_id = 1
    secret = json.load(open('./settings/secret_setting.json', 'r'))['SECRET']
    api_url = secret['FIREBASE']['R_DB']['URL']

    def build(self):
        self.my_firebase = MyFirebase()
        return GUI

    def on_start(self):
        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
            # 新しいidTokenと，アプリ起動者のlocal_id(user_id的なもの)を取得するためにrefreshTokenを使う
            id_token, local_id = self.my_firebase.exchange_refresh_token(
                refresh_token)

            # dbからデータ取得(idTokenを付与することでdbの読み取り/書き込みが可能に)
            result = requests.get(
                f"{self.api_url}{local_id}.json?auth={id_token}")
            print(result.ok)
            print(result.json())
            data = json.loads(result.content.decode())

            # アバターをicons/avatarsから取得
            avatar_gird = self.root.ids["change_avatar_screen"].ids["avatar_grid"]
            for root_dir, folders, files in walk("icons/avatars"):
                for f in files:
                    img = ImageButton(source="icons/avatars/"+f,
                                      on_release=partial(self.change_avatar, f))
                    avatar_gird.add_widget(img)

            # streakラベルをDBのdataから設定
            streak_label = self.root.ids["home_screen"].ids["streak_label"]
            streak_label.text = str(data['streak']) + " Day Streak!"

            # 自分のフレンドIDを
            # 設定
            friend_id_label = self.root.ids["settings_screen"].ids["friend_id_label"]
            friend_id_label.text = "Friend ID: " + str(self.my_friend_id)

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

            self.root.ids["screen_manager"].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids["screen_manager"].transition = CardTransition()

        except:
            pass

    def change_avatar(self, image, widget_id):
        # アプリ内のアバターを変更する
        avatar_image = self.root.ids["avatar_image"]
        avatar_image.source = "icons/avatars/" + image
        # firebaseのアバターを変更する
        my_data = '{"avatar":"%s"}' % image
        requests.patch(f"{self.api_url}{self.my_friend_id}.json", data=my_data)
        # 設定画面に戻る
        self.change_screen("settings_screen")

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        # rootはmain.kvのGridLayout(rootウィジェット)のこと
        screen_manager.current = screen_name
        # 現在のスクリーンを変更する


MainApp().run()
