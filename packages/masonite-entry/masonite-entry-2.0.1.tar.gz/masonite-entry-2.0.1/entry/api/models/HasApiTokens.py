import uuid
from entry.api.models.Token import Token

class HasApiTokens:
    """
        Helper Class For API Authentication Models
    """


    def prevent_scopes(self):
        pass


    def grant_scopes(self):
        pass


    def create_token(self, name='default', scopes=''):
        """ Create a new API token and save to model """

        if isinstance(self.grant_scopes(), list):
            scopes = self.grant_scopes()

        if isinstance(scopes, list):
            if isinstance(self.prevent_scopes(), list):
                scopes = set(scopes) - set(self.prevent_scopes())
            scopes = ' '.join(scopes)
        else:
            if isinstance(self.prevent_scopes(), list):
                scopes = scopes.split(' ')
                scopes = set(scopes) - set(self.prevent_scopes())
                scopes = ' '.join(scopes)

        generated_token = uuid.uuid4().hex

        user_by_token = Token.where('user_id', self.id).first()

        if user_by_token:
            # update the token
            user_by_token.token = generated_token
            user_by_token.scope = scopes
            user_by_token.save()
        else:
            Token.create(
                user_id = self.id,
                name = name,
                scope = scopes,
                token = generated_token
            )

        return generated_token


    def get_token(self):
        """ Get current API Token """
        return Token.where('user_id', self.id).first().token


    def has_token(self):
        """ Check if user has an API token """

        if Token.where('user_id', self.id).first():
            return True
        
        return False
    
    def has_scope(self, scope):
        get_token = Token.where('user_id', self.id).first()
        
        if get_token:
            scopes = get_token.scope.split(' ')
            if scope in scopes:
                return True
        return False
    
    def add_scopes(self, *scopes):
        get_token = Token.where('user_id', self.id).first()
        
        if get_token:
            scopes = ' '.join(scopes)
            get_token.scope += scopes
            return get_token.save()

        return False
    

    def set_scopes(self, *scopes):
        get_token = Token.where('user_id', self.id).first()
        get_token.scope = ''
        get_token.save()
        return self.add_scopes(scopes)


    def with_token(self, token):
        """ Set API token for the current user """
        self.token = token
        return self
    
    def revoke_token(self):
        get_token = Token.where('user_id', self.id).first()
        if get_token:
            return get_token.delete()
        
        return False
