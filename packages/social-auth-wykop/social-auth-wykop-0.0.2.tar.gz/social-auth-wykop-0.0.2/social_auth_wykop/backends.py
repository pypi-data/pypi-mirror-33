import base64
import hashlib
import json
import urllib
import wykop

from social_core.backends.legacy import LegacyAuth
from social_core.exceptions import AuthMissingParameter


class WykopAPIv1(LegacyAuth):
    name = 'wykop'
    ID_KEY = 'connectData'
    GET_ALL_EXTRA_DATA = True

    def get_user_id(self, details, response):
        return details.get('login')

    def auth_url(self):
        client_id, client_secret = self.get_key_and_secret()
        redirect_Url = self.strategy.absolute_uri(self.redirect_uri).encode('utf-8')
        url = 'http://' + wykop.WykopAPI._domain + '/user/connect/' + 'appkey/' + client_id + '/'
        url += 'redirect/' + urllib.parse.quote_plus(base64.b64encode(redirect_Url)) + '/'
        url += 'secure/' + hashlib.md5(client_secret.encode('utf-8') + redirect_Url).hexdigest()

        return url

    def uses_redirect(self):
        return True

    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance"""
        if self.ID_KEY not in self.data:
            raise AuthMissingParameter(self, self.ID_KEY)
        data = json.loads(base64.b64decode(self.data['connectData']).decode('utf-8'))
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        user = wykop.WykopAPI(*self.get_key_and_secret()).get_profile(response.get('login'))
        return dict(username=user['login'], **user)

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        return details
