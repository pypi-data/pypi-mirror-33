''' Load User Middleware'''
from entry.api.auth import JWTAuthentication

class JWTMiddleware:
    ''' Middleware class which loads the current user into the request '''

    def __init__(self, Request):
        ''' Inject Any Dependencies From The Service Container '''
        self.request = Request
        self.jwt = JWTAuthentication()
        self.jwt.request = self.request

    def before(self):
        ''' Run This Middleware Before The Route Executes '''
        self.jwt.authenticate()

    def after(self):
        ''' Run This Middleware After The Route Executes '''
        pass
