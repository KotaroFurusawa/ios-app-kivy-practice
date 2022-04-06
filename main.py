from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from workoutbanner import WorkoutBanner
from friendbanner import FriendBanner
from functools import partial
from specialbuttons import ImageButton, LabelButton
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


class AddFriendScreen(Screen):
    pass


class FriendsListScreen(Screen):
    pass


class AddWorkoutScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class FriendWorkoutScreen(Screen):
    pass


GUI = Builder.load_file("main.kv")


class MainApp(App):
    my_friend_id = 1
    workout_image = None
    option_choice = None
    secret = json.load(open('./settings/secret_setting.json', 'r'))['SECRET']
    api_url = secret['FIREBASE']['R_DB']['URL']

    def build(self):
        self.my_firebase = MyFirebase()
        return GUI

    def update_workout_image(self, filename, widget_id):
        self.workout_image = filename

    def on_start(self):
        # アバターをicons/avatarsから取得
        avatar_gird = self.root.ids["change_avatar_screen"].ids["avatar_grid"]
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButton(source="icons/avatars/"+f,
                                  on_release=partial(self.change_avatar, f))
                avatar_gird.add_widget(img)

        # workoutイメージをicons/workoutsから取得
        workout_image_gird = self.root.ids["add_workout_screen"].ids["workout_image_grid"]
        for root_dir, folders, files in walk("icons/workouts"):
            for f in files:
                if '.png'in f:
                    img = ImageButton(source="icons/workouts/"+f,
                                      on_release=partial(self.update_workout_image, f))
                    workout_image_gird.add_widget(img)

        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
            # 新しいidTokenと，アプリ起動者のlocal_id(user_id的なもの)を取得するためにrefreshTokenを使う
            id_token, local_id = self.my_firebase.exchange_refresh_token(
                refresh_token)
            self.local_id = local_id  # これによって他のメソッドでもlocal_idが使える
            self.id_token = id_token
            # dbからデータ取得(idTokenを付与することでdbの読み取り/書き込みが可能に)
            result = requests.get(
                f"{self.api_url}{local_id}.json?auth={id_token}")
            print(f"token{result.ok}")
            print(result.json())
            data = json.loads(result.content.decode())

            # friendListをDBから取得
            self.friends_list = data["friends"]

            # friendListの友達を表示
            friends_list_array = self.friends_list.split(",")[1:]
            for friend in friends_list_array:
                friend = friend.replace(" ", "")
                friend_banner = FriendBanner(friend_id=friend)
                self.root.ids['friends_list_screen'].ids['friends_list_grid'].add_widget(
                    friend_banner)
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
            workouts = data["workouts"]
            if workouts != "":
                workout_keys = list(workouts.keys())

                for workout_key in workout_keys:
                    workout = workouts[workout_key]
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

        except Exception as e:
            print(e)
            pass

    def add_friend(self, friend_id):
        # friend_idが存在するか確かめる。
        check_req = requests.get(
            self.api_url+'.json?orderBy="my_friend_id"&equalTo='+friend_id)
        data = check_req.json()
        if data == {}:
            # 存在しない場合はその旨を表示
            self.root.ids["add_friend_screen"].ids['add_friend_label'].text = "Invalid friend ID"
        else:
            # 存在すればsuccessと表示し，フレンドリストに追加する
            key = list(data.keys())[0]
            new_friend_id = data[key]['my_friend_id']
            print(new_friend_id)
            self.root.ids["add_friend_screen"].ids[
                'add_friend_label'].text = f"Friend ID {friend_id} added successfully."

            self.friends_list = f"{self.friends_list},{friend_id}"
            patch_data = '{"friends":"%s"}' % self.friends_list
            patch_req = requests.patch(
                self.api_url+self.local_id+".json?auth="+self.id_token, data=patch_data)
            print(patch_req.ok)
            print(patch_req.json())

    def change_avatar(self, image, widget_id):
        # アプリ内のアバターを変更する
        avatar_image = self.root.ids["avatar_image"]
        avatar_image.source = "icons/avatars/" + image
        # firebaseのアバターを変更する
        my_data = '{"avatar":"%s"}' % image
        requests.patch(f"{self.api_url}{self.my_friend_id}.json", data=my_data)
        # 設定画面に戻る
        self.change_screen("settings_screen")

    def add_workout(self):
        # add workout screenで選択されたすべてのデータを取得する
        workout_ids = self.root.ids['add_workout_screen'].ids
        # すでに，変数self.workout_imageにworkout_imageは指定されている(workout画像選択時，on_releaseにて)
        description_input = workout_ids['description_input'].text
        # すでにoption_choice関数によって(Time or set or distance)は指定されている
        quantity_input = workout_ids['quantity_input'].text
        units_input = workout_ids['units_input'].text
        month_input = workout_ids['month_input'].text
        day_input = workout_ids['day_input'].text
        year_input = workout_ids['year_input'].text

        # 入力項目に空欄がないか確認する
        if self.workout_image == None:
            print("comeback_to_this")
            return
        # descriptionに空白がある場合は許可する
        if self.option_choice == None:
            workout_ids['time_label'].color = 1, 0, 0, 1
            workout_ids['distance_label'].color = 1, 0, 0, 1
            workout_ids['sets_label'].color = 1, 0, 0, 1
            return
        try:
            int_quantity = float(quantity_input)
        except:
            # 何も入力されていない場合、背景を赤くする
            workout_ids['quantity_input'].background_color = 1, 0, 0, 1
            return

        if units_input == "":
            workout_ids['units_input'].background_color = 1, 0, 0, 1
            return

        try:
            int_month = int(month_input)
        except:
            workout_ids['month_input'].background_color = 1, 0, 0, 1
            return

        try:
            int_day = int(day_input)
        except:
            workout_ids['day_input'].background_color = 1, 0, 0, 1
            return

        try:
            int_year = int(year_input)
        except:
            workout_ids['year_input'].background_color = 1, 0, 0, 1
            return

        # もし、OKならFireBaseにpostする
        workout_payload = {"workout_img": self.workout_image, "description": description_input,
                           "likes": 0, "number": float(quantity_input), "type_image": self.option_choice,
                           "units": units_input, "date": month_input+"/"+day_input+"/20"+year_input}
        workout_request = requests.post(
            f"{self.api_url}{self.local_id}/workouts.json?auth={self.id_token}", data=json.dumps(workout_payload))
        print(workout_request.json())

    def load_friend_workout_screen(self, friend_id, widget):
        # friend_idを用いて、DBから友人のworkoutを取得する
        friend_data_req = requests.get(
            self.api_url+'.json?orderBy="my_friend_id"&equalTo='+friend_id)
        friend_data = friend_data_req.json()
        workouts = list(friend_data.values())[0]['workouts']
        friend_banner_grid = self.root.ids['friend_workout_screen'].ids['friend_banner_grid']

        # friend_banner_gridからすべてのwidgetを削除する
        # これをしないと，前回呼び出したworkoutに加えてworkoutが表示されてしまう．
        for w in friend_banner_grid.walk():
            # WorkoutBannerクラスで生成されたwidgetのみ削除
            if w.__class__ == WorkoutBanner:
                friend_banner_grid.remove_widget(w)

        # friend_workout_screenを表示
        if workouts != "":
            for key in list(workouts.keys()):
                workout = workouts[key]
                print(key, workout)
                w = WorkoutBanner(
                    workout_img=workout["workout_img"],
                    description=workout["description"],
                    type_image=workout["type_image"],
                    number=workout["number"],
                    units=workout["units"],
                    likes=workout["likes"])
                friend_banner_grid.add_widget(w)

        # streak labelを追加する
        friend_streak_label = self.root.ids['friend_workout_screen'].ids['friend_streak_label']
        friend_streak_label.text = f"{list(friend_data.values())[0]['streak']} Day Streak!"
        # friend_workout_screenに変更を加える
        self.change_screen("friend_workout_screen")

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        # rootはmain.kvのGridLayout(rootウィジェット)のこと
        screen_manager.current = screen_name
        # 現在のスクリーンを変更する


MainApp().run()
