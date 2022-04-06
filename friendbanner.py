from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from specialbuttons import ImageButton, LabelButton
from kivy.app import App
from functools import partial
import kivy.utils
import requests
import json
from kivy.graphics import Color, Rectangle


class FriendBanner(FloatLayout):
    secret = json.load(open('./settings/secret_setting.json', 'r'))['SECRET']
    api_url = secret['FIREBASE']['R_DB']['URL']

    def __init__(self, **kwargs):
        super(FriendBanner, self).__init__()
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#67697C")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # ↓pythonで色を変更する場合は，これを書かないとupdateされない
        self.bind(pos=self.update_rect, size=self.update_rect)

        # 友達のアバターを追加
        check_req = requests.get(
            self.api_url+'.json?orderBy="my_friend_id"&equalTo='+kwargs['friend_id'])
        data = check_req.json()
        unique_identifier = list(data.keys())[0]
        their_avatar = data[unique_identifier]['avatar']

        image_button = ImageButton(
            source="icons/avatars/"+their_avatar, size_hint=(.3, 1), pos_hint={"top": 1, "right": 0.4}, on_release=partial(App.get_running_app().load_friend_workout_screen, kwargs['friend_id']))

        # 友達のIDを追加
        friend_label = LabelButton(
            text=kwargs['friend_id'], size_hint=(.6, 1), pos_hint={"top": 1, "right": 1})

        self.add_widget(image_button)
        self.add_widget(friend_label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
