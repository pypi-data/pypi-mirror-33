''' A OAuthToken Database Model '''
from config.database import Model

class Token(Model):
    __table__ = 'oauth_tokens'

    __fillable__ = ['user_id', 'token', 'code', 'refresh_token', 'expires_at', 'scopes']