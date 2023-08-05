""" An ApiProvider Service Provider """
import os

from entry.commands.InstallCommand import InstallCommand
from entry.commands.ResourceCommand import ResourceCommand
from entry.commands.PublishCommand import PublishCommand
from masonite.packages import create_controller
from masonite.provider import ServiceProvider
from routes import api

package_directory = os.path.dirname(os.path.realpath(__file__))

class ApiProvider(ServiceProvider):

    def register(self):
        self.app.bind('ResourceRoutes', api.RESOURCES)
        self.app.bind('InstallCommand', InstallCommand())
        self.app.bind('ResourceCommand', ResourceCommand())
        self.app.bind('PublishCommand', PublishCommand())
        # self.app.make('RouteMiddleware').update({
        #     'jwt': 'entry.api.middleware.JWTMiddleware'
        # })
        self.app.bind(
            'Entry_MigrationDirectory',
            os.path.join(package_directory, '../migrations')
        )


    def boot(self, Response, ResourceRoutes, Route, Request, Headers):
        router = Route
        if Response == 'Route not found. Error 404':

            """
            |--------------------------------------------------------------------------
            | Pull in the API Routes from the Service Container
            |--------------------------------------------------------------------------
            |
            | The Service Container has loaded all Api routes into the container so
            | let's loop through and check for any matches.
            |
            """

            for route in ResourceRoutes:

                """
                |--------------------------------------------------------------------------
                | If We've Got A Match
                |--------------------------------------------------------------------------
                |
                | If we have a match then let's go ahead and execute the route, load the 
                | response into the data variable and get on with our lives.
                |
                """

                if route.url in router.url:
                    data = route.load_request(Request).load_container(self.app).handle()

                    if data:
                        self.app.bind('Response', data)
                        Headers += [
                            ("Content-Type", "application/json; charset=utf-8")
                        ]
                        break
                    else:
                        data = 'Route not found. Error 404'
                else:
                    data = 'Route not found. Error 404'
