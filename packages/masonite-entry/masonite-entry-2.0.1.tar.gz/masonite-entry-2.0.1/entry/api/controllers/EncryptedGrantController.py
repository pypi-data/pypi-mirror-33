''' A Module Description '''
from masonite.facades.Auth import Auth
from masonite.request import Request
from cryptography.fernet import Fernet
from masonite.auth import Sign
import pendulum
import json
from entry.helpers import expiration_time
from masonite.helpers.routes import get, post


class EncryptedGrantController:
    ''' Class Docstring Description '''

    __auth__ = Auth

    def generate(self, request: Request):
        # generate a secret key and sign it based on your server secret key
        if not request.has('username') or not request.has('password'):
            return {'error': 'This API call requires a username and password in the payload.'}

        user = self.__auth__(request).login(request.input(
            'username'), request.input('password'))
        
        if user:
            # user is authenticated
            if request.has('scope'):
                scopes = request.input('scope')
            else:
                scopes = ''

            # generate a new key and signed with the secret key
            payload = {
                'issued': str(pendulum.now()),
                'expires_at': str(pendulum.now().add(days=1)),
                'scope': scopes
            }

            return {'token': Sign().sign(json.dumps(payload))}

        request.status('401 Unauthorized')
        return {'error': 'Username or password do not match'}

    def refresh(self, request: Request):
        if not request.input('token'):
            return {'error': 'No Token Found'}

        try:
            token = Sign().unsign(request.input('token'))
        except:
            return {'error': 'Could not decode token'}


        # generate a new key and signed with the secret key
        payload = {
            'issued': str(pendulum.now()),
            'expires': str(pendulum.now().add(days=1))
        }

        return {'token': Sign().sign(json.dumps(payload))}
    
    @staticmethod
    def routes():
        try:
            return [
                get('/encrypt/token', EncryptedGrantController.generate),
                post('/encrypt/refresh', EncryptedGrantController.refresh),
            ]
        except ImportError as e:
            print("\033[93mWarning: could not find app.http.controllers.Entry.Api - Error {0}".format(e))
        
        return []