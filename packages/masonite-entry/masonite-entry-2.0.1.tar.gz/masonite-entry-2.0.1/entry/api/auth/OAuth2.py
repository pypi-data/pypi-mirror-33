from entry.api.exceptions import NoApiTokenFound, InvalidToken, PermissionScopeDenied, ExpiredToken
from entry.api.models.Token import Token
import pendulum

class OAuth2:
    authentication_model = None
    token_model = Token
    scopes = ['*']

    def authenticate(self):
        # get the token
        token = self.request.input('token')
        if not token:
            raise NoApiTokenFound

        client_token = self.token_model.where('token', token).first()

        if not client_token:
            raise InvalidToken
        
        # Check correct scopes:
        scopes = client_token.scopes.split(' ')

        if '*' not in self.scopes:
            if not set(self.scopes).issubset(scopes):
                raise PermissionScopeDenied
        
        if pendulum.parse(str(client_token.expires_at)).is_past():
            raise ExpiredToken
        
        