import base64
import hashlib
import json
import urllib
import wykop
import binascii

from requests import HTTPError, Response

from social_core.backends.legacy import LegacyAuth
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthMissingParameter
from social_core.utils import handle_http_errors
from wykop.api.exceptions import InvalidCredentialsError


class WykopAPIv1(LegacyAuth):
    name = 'wykop'
    ID_KEY = 'login'
    GET_ALL_EXTRA_DATA = True

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
        if 'connectData' not in self.data:
            raise AuthMissingParameter(self, self.ID_KEY)
        data = json.loads(base64.b64decode(self.data['connectData']).decode('utf-8'))
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        user = wykop.WykopAPI(*self.get_key_and_secret()).get_profile(response.get('login'))
        return dict(username=user['login'], **user)

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        return details


class WykopAPIv1_FakeOAuth2(BaseOAuth2):
    """
    Fake OAuth2 API. Use it to support django-rest-framework-social-oauth2
    """

    name = 'wykop'
    STATE_PARAMETER = False
    REDIRECT_STATE = False
    ID_KEY = 'login'

    def auth_url(self):
        client_id, client_secret = self.get_key_and_secret()
        redirect_Url = self.strategy.absolute_uri(self.redirect_uri).encode('utf-8')
        url = 'http://' + wykop.WykopAPI._domain + '/user/connect/' + 'appkey/' + client_id + '/'
        url += 'redirect/' + urllib.parse.quote_plus(base64.b64encode(redirect_Url)) + '/'
        url += 'secure/' + hashlib.md5(client_secret.encode('utf-8') + redirect_Url).hexdigest()

        return url

    def get_access_token_from_connectData(self, connected_data):
        return json.loads(base64.b64decode(connected_data).decode('utf-8'))['token']

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance"""
        if 'connectData' not in self.data:
            raise AuthMissingParameter(self, 'connectData')
        response = json.loads(base64.b64decode(self.data['connectData']).decode('utf-8'))
        kwargs.update({'response': response, 'backend': self})

        return self.do_auth(response['token'], *args, **kwargs)

    def get_user_details(self, response):
        user = wykop.WykopAPI(*self.get_key_and_secret()).get_profile(response.get('login'))
        return dict(username=user['login'], **user)

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service. Implement in subclass"""

        if access_token.startswith('connectData:'):
            try:
                access_token = self.get_access_token_from_connectData(access_token.replace("connectData:", ""))
            except (UnicodeDecodeError, binascii.Error) as e:

                msg = 'Token has invalid format, {}'.format(str(e))
                response = Response()
                response.status_code = 400
                response._content = json.dumps({"error": {"message": msg}}).encode('utf-8')
                raise HTTPError(msg, response=response)

        api = wykop.WykopAPI(*self.get_key_and_secret())
        try:
            return api.user_login(login='', accountkey=access_token)
        except InvalidCredentialsError as exception:

            msg = ";".join([err.decode('utf-8') for err in exception.args])

            response = Response()
            response.status_code = 401
            response._content = json.dumps({"error": {"message": msg}}).encode('utf-8')

            raise HTTPError(msg, response=response)

    def do_auth(self, access_token, *args, **kwargs):
        data = self.user_data(access_token, *args, **kwargs)
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        return details
