''' A OAuthToken Database Model '''
from config.database import Model

class OAuthToken(Model):
    __table__ = 'oauth_tokens'

    __fillable__ = ['user_id', 'name', 'token', 'scope']
