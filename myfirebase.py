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
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)

            # localIdをmain app classに保存する
            app.localId = localId

            # idTokenをmain app classに保存する
            app.idToken = idToken

            # firebaseからnext friend idを取得
            # next_friend_idは次作成されるユーザーの登録番号nのこと(次のユーザーはn人目の登録者)
            friend_get_req = requests.get(
                self.api_url+"next_friend_id.json?auth="+idToken)
            my_friend_id = friend_get_req.json()
            friend_patch_data = '{"next_friend_id":%s}' % str(my_friend_id+1)
            frined_patch_req = requests.patch(
                self.api_url+".json?auth="+idToken, data=friend_patch_data)

            # frined_id = friend_get_req.json()[]
            # localIdから新しくkeyを生成しdbに保存する
            my_data = '{"avatar": "man.png", "friends": "", "workouts": "","streak":"0","my_friend_id":%s}' % my_friend_id
            post_request = requests.patch(
                f"{self.api_url}{localId}.json?auth=" + idToken, data=my_data)

            app.change_screen("home_screen")

        if not sign_up_request.ok:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]["message"]

            app.root.ids['login_screen'].ids['login_message'].text = error_message

    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key="+self.wak
        refresh_payload = '{"grant_type":"refresh_token","refresh_token":"%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        print(refresh_req.ok)
        print(refresh_req.json())

        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id
