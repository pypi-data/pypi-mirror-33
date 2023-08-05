from masonite.auth import Sign
from masonite.facades import Auth
from masonite.view import View
from masonite.helpers.routes import get, post
import pendulum
import json
from entry.api.models.Scope import Scope
from entry.api.models.Application import Application
from entry.api.models.Token import Token
from urllib.parse import urlencode
import uuid
import pendulum

from masonite.request import Request

class OAuth2Controller:

    __application__ = Application
    __token__ = Token
    __scope__ = Scope

    def __init__(self):
        pass
    
    def show(self, request: Request, view: View):
        client_id = request.input('client_id')
        redirect_uri = request.input('redirect_uri')
        if request.has('state'):
            state = request.input('state')
        else:
            state = ''

        # Find Application
        client = self.__application__.where('client_id', client_id).first()

        scopes = []
        if request.has('scope'):
            for scope in request.input('scope').split(' '):
                db_scope = self.__scope__.where('name', scope).first()
                if db_scope:
                    scopes.append(db_scope)
        
        return view.render('/entry/views/oauth2', {'scopes': scopes, 'app_name': client.name, 'app_description': client.description, 'redirect_uri': redirect_uri, 'state': state})
    
    def send(self, request: Request):
        scopes = []
        for value in request.all():
            if value.startswith('scope-'):
                scopes.append(value.replace('scope-', ''))

        code = uuid.uuid4().hex

        if request.has('state'):
            state = request.input('state')
        else:
            state = ''

        self.__token__.create(
            user_id = request.user().id,
            token = "{}".format(uuid.uuid4().hex),
            code = code,
            refresh_token = "{}{}".format(uuid.uuid4().hex, uuid.uuid4().hex),
            expires_at = pendulum.now().add(days=1).to_datetime_string(),
            refresh_expires_at = pendulum.now().add(days=7).to_datetime_string(),
            scopes = ' '.join(scopes)
        )

        return request.redirect('{0}?code={1}&state={2}'.format(request.input('redirect_uri'), code, state))

    def refresh(self, request: Request):
        
        grant_type = request.input('grant_type')
        refresh_token = request.input('refresh_token')

        if grant_type != 'refresh_token' or not refresh_token:
            return {'error': "Invalid refresh token or grant type given."}
        
        token = self.__token__.where('refresh_token', refresh_token).first()

        if token:
            if pendulum.parse(str(token.refresh_expires_at)).is_past():
                return {'error': 'Refresh token expired'}

            token.token = "{}".format(uuid.uuid4().hex)
            token.expires_at = pendulum.now().add(days=1).to_datetime_string(),
            token.refresh_token = "{}{}".format(uuid.uuid4().hex, uuid.uuid4().hex)
            token.refresh_expires_at = pendulum.now().add(days=7).to_datetime_string()
            token.save()

            return {
                "access_token": token.token,
                "token_type": "Bearer",
                "expires_at": token.expires_at[0],
                "refresh_token": token.refresh_token,
                "scope": token.scopes
            }
        
        return {'error': 'Invalid Token'}

    
    def authorize(self, request: Request):
        client_id = request.input('client_id')
        client_secret = request.input('client_secret')
        grant_type = request.input('grant_type')
        code = request.input('code')
        redirect_uri = request.input('redirect_uri')

        client = self.__application__.where('client_id', client_id).first()

        if client.client_secret != client_secret:
            return {'error': 'client secret does not match'}
        
        token = self.__token__.where('code', code).first()

        if not token:
            return {'error': 'Token does not exist'}
        
        if token.code != request.input('code'):
            return {'error': 'Invalid token'}

        return {
            "access_token": token.token,
            "token_type": "Bearer",
            "expires_at": token.expires_at,
            "refresh_token": token.refresh_token,
            "scope": token.scopes
        }

    def revoke(self):
        pass
    
    @staticmethod
    def routes(self):
        return [
            get('/oauth2/token', OAuth2Controller.send),
            post('/oauth2/authorize', OAuth2Controller.authorize),
            post('/oauth2/refresh', OAuth2Controller.refresh),
        ]
