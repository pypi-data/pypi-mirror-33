import os
import subprocess
from cleo import Command
from masonite.packages import create_controller, append_web_routes, append_api_routes


package_directory = os.path.dirname(os.path.realpath(__file__))

class PublishCommand(Command):
    """
    Installs needed controllers and routes into a Masonite project

    entry:publish
        {--c|controller=None : Name of the controller you want to public}
        {--a|auth=None : Name of the controller you want to public}
        {--p|path=None : The location you want to publish to}
    """

    def handle(self):

        if self.option('controller') != 'None':

            path = self.option('path')
            if path == 'None':
                path = 'app/http/controllers/entry'

            create_controller(
                os.path.join(package_directory,
                            '../api/controllers/{0}.py'.format(self.option('controller'))),
                to=path
            )

        if self.option('auth') != 'None':

            path = self.option('path')
            if path == 'None':
                path = 'app/http/auth/entry'

            create_controller(
                os.path.join(package_directory,
                            '../api/auth/{0}.py'.format(self.option('auth'))),
                to=path
            )
