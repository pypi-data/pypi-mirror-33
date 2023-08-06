import json
import os
import requests


class OAuthUtils:

    def __init__(self):
        self.headers = {'Content-type': 'application/json'}

        self.url = 'https://factern-test.eu.auth0.com/oauth/token'

        self.data = {
            "client_id": "iGqdQKPPvrt52GiBRk6DqFwGHWTV5o9y",
            "client_secret": os.environ['FACTERN_CLIENT_SECRET'],
            "audience": "https://api.factern.com",
            "grant_type": "client_credentials"
        }

    def get_auth_token(self):

        resp = requests.post(
            self.url,
            data=json.dumps(self.data),
            headers=self.headers
        )

        return json.loads(resp.text)['access_token']

if __name__ == '__main__':
    oauth = OAuthUtils()
    print(oauth.get_auth_token())
