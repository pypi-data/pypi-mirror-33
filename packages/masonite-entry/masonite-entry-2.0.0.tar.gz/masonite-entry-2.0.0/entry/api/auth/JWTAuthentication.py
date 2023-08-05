from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound, PermissionScopeDenied, InvalidToken, ExpiredToken
from urllib.parse import parse_qs
from masonite.routes import Post, Delete
from entry.api.models.OAuthToken import OAuthToken
from masonite.auth import Sign
from entry.helpers import expiration_time
import pendulum
import json
import jwt
from jwt.exceptions import DecodeError
from config import application


class JWTAuthentication:
    scopes = ['*']
    expires_in = '5 minutes'

    def authenticate(self):
        # Find which input has the authorization token:
        token = self.get_token()

        try:
            decoded_token = jwt.decode(token, application.KEY, algorithms=['HS256'])
        except DecodeError:
            raise InvalidToken
        
        if not self.check_time(decoded_token):
            raise ExpiredToken

        # Check correct scopes:
        scopes = decoded_token['scope'].split(' ')
        if '*' not in self.scopes:
            if not set(self.scopes).issubset(scopes):
                raise PermissionScopeDenied

        # Delete the token input
        if self.request.has('token') and self.request.is_not_get_request():
            build_new_inputs = {}
            for i in self.request.request_variables:
                build_new_inputs[i] = self.request.request_variables[i]
            
            build_new_inputs.pop('token')
            self.request.request_variables = build_new_inputs

    def get_token(self):
        if self.request.has('token'):
            return self.request.input('token')
        elif self.request.header('AUTHORIZATION'):
            return self.request.header('AUTHORIZATION').replace('Bearer ', '')
        
        # Check if Authentication token exists
        if not self.request.header('AUTHORIZATION') and not self.request.has('token'):
            raise NoApiTokenFound
  
    def check_time(self, unsign_token):
        issued_time = unsign_token['issued']
        minutes_ago = expiration_time(self.expires_in, subtract=True)

        expiration = self.expires_in.split(' ')
        expiration_amount = int(expiration[0])

        time_parse = minutes_ago.diff(pendulum.parse(issued_time))

        if pendulum.parse(unsign_token['expires']).is_past():
            return False
        
        return True
        
    @staticmethod
    def routes():
        try:
            return [
                Post().route('/oauth/token', JWTAuthentication.authenticate),
            ]
        except ImportError as e:
            print("\033[93mWarning: could not find app.http.controllers.Entry.Api - Error {0}".format(e))
        
        return []
