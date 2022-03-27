import requests
import json
from kivy.app import App


class MyFirebase():
    secret = json.load(open('./settings/secret_setting.json', 'r'))['SECRET']
    wak = secret['FIREBASE']['WEB_API_KEY']
    api_url = secret['FIREBASE']['R_DB']['URL']

    def sign_up(self, email, password):
        app = App.get_running_app()  # main App
        # firebaseにemailとpasswordを送る
        # firebaseはlocalId，authToken,refreshTokenを返す
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key="+self.wak
        signup_payload = {"email": email,
                          "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())

        if sign_up_request.ok:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']

            # ファイルにfreshTokenを保存する
            with open("refres_token.txt", "w") as f:
                f.write(refresh_token)
            # localIdをmain app classに保存する
            app.localId = localId
            # idTokenをmain app classに保存する
            app.idToken = idToken
            # localIdから新しくkeyを生成しdbに保存する
            my_data = '{"avatar": "man.png", "friends": "", "workouts": ""}'
            post_request = requests.patch(
                f"{self.api_url}{localId}.json?auth=" + idToken, data=my_data)
            print(post_request.ok)
            print(json.loads(post_request.content.decode()))

            app.change_screen("home_screen")

        if not sign_up_request.ok:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]["message"]

            app.root.ids['login_screen'].ids['login_message'].text = error_message

    def sign_in(self):
        pass
