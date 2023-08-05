''' A Module Description '''
from masonite.facades.Auth import Auth
from masonite.helpers.routes import get, post
from masonite.request import Request
import pendulum
import jwt
from config import application


class JWTGrantController:
    ''' JWT Controller '''

    __config__ = application
    __auth__ = Auth

    def generate(self, Request):
        if not Request.has('username') or not Request.has('password'):
            return {'error': 'This API call requires a username and password in the payload.'}

        user = self.__auth__(Request).login(
            Request.input('username'), 
            Request.input('password')
        )

        if Request.has('scope'):
            scope = Request.input('scope')
        else:
            scope = ''

        if user:
            # get the current time
            current_time = str(pendulum.now())

            payload = {
                'issued': current_time,
                'scope': scope,
                'expires': str(pendulum.now().add(minutes=5))
            }

            encoded = jwt.encode(payload, self.__config__.KEY, algorithm='HS256').decode('UTF-8')
            return {'token': encoded}
        else:
            return {'error': 'Incorrect username or password'}
    
    def refresh(self, request: Request):
        try:
            decoded_token = jwt.decode(request.input('token'), application.KEY, algorithms=['HS256'])
        except DecodeError:
            return {'error': 'Could not decode token'}

        payload = {
            'issued': str(pendulum.now()),
            'scope': decoded_token['scope'],
            'expires': str(pendulum.now().add(minutes=5))
        }

        encoded = jwt.encode(payload, application.KEY, algorithm='HS256').decode('UTF-8')
        return {'token': encoded}

    @staticmethod
    def routes():
        return [
            get('/jwt/authenticate', JWTGrantController.generate),
            post('/jwt/refresh', JWTGrantController.refresh)
        ]