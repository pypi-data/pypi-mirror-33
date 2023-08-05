from entry.api.exceptions import ApiNotAuthenticated, NoApiTokenFound, PermissionScopeDenied
from urllib.parse import parse_qs
from masonite.routes import Post, Delete
from entry.api.models.OAuthToken import OAuthToken


class TokenAuthentication:

    authentication_model = OAuthToken
    scopes = ['*']

    def authenticate(self):

        # Find which input has the authorization token:
        if self.request.has('token'):
            token = self.request.input('token')
        elif self.request.header('AUTHORIZATION'):
            token = self.request.header('AUTHORIZATION').replace('Bearer ', '')

        if not self.authentication_model:
            self.authentication_model = self.model

        # Check if Authentication token exists
        if not self.request.header('AUTHORIZATION') and not self.request.has('token'):
            raise NoApiTokenFound

        if not self.authentication_model.where('token', token).count():
            raise ApiNotAuthenticated
        
        # Check correct scopes:
        if '*' not in self.scopes:
            scopes = self.authentication_model.where('token', token).first().scope.split(' ')
            
            if not set(self.scopes).issubset(scopes):
                raise PermissionScopeDenied

        # Delete the token input
        if self.request.has('token') and self.request.is_not_get_request():
            build_new_inputs = {}
            for i in self.request.request_variables:
                build_new_inputs[i] = self.request.request_variables[i]
            
            build_new_inputs.pop('token')
            self.request.params = build_new_inputs
    
        
    def tokens_from_model(self, model):
        self.authentication_model = model
        return self
    

    @staticmethod
    def routes():
        try:
            return [
                Post().module('app.http.controllers.Entry.Api').route('/oauth/token', 'OAuthPasswordGrantController@generate'),
                Delete().module('app.http.controllers.Entry.Api').route('/oauth/token', 'OAuthPasswordGrantController@revoke'),
            ]
        except ImportError as e:
            print("\033[93mWarning: could not find app.http.controllers.Entry.Api - Error {0}".format(e))
        
        return []
