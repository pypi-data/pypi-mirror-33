from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound, PermissionScopeDenied, InvalidToken
from urllib.parse import parse_qs
from masonite.routes import Post, Delete
from entry.api.models.OAuthToken import OAuthToken
from masonite.auth import Sign
from entry.helpers import expiration_time
import pendulum
import json
from cryptography.fernet import InvalidToken as InvalidDecryption


class EncryptedTokenAuthentication:
    scopes = ['*']
    expires_in = '5 minutes'

    def authenticate(self):
        # Find which input has the authorization token:

        token = self.get_token()

        try:
            unsign_token = json.loads(Sign().unsign(token))
        except InvalidDecryption:
            raise InvalidToken

        if not self.check_time(unsign_token):
            raise ApiNotAuthenticated

        # Check correct scopes:
        scopes = unsign_token['scope'].split(' ')
        print(scopes)

        if '*' not in self.scopes:
            if not set(self.scopes).issubset(scopes):
                raise PermissionScopeDenied


    def get_token(self):
        if self.request.has('token'):
            return self.request.input('token')
        elif self.request.header('AUTHORIZATION'):
            return self.request.header('AUTHORIZATION').replace('Bearer ', '')
        
        # Check if Authentication token exists
        if not self.request.header('AUTHORIZATION') and not self.request.has('token'):
            raise NoApiTokenFound
  
    def check_time(self, unsign_token):
        issued_time = unsign_token['expires_at']

        if pendulum.parse(issued_time).is_past():
            return False
        
        return True
