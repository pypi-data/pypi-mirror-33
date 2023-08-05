import os
import subprocess
from cleo import Command
from masonite.packages import create_controller, append_web_routes, append_api_routes


package_directory = os.path.dirname(os.path.realpath(__file__))

class InstallCommand(Command):
    """
    Installs needed controllers and routes into a Masonite project

    entry:install
    """

    def handle(self):
        
        create_controller(
            os.path.join(package_directory,
                         '../entry_snippets/controllers/OAuthPasswordGrantController.py'),
            to='app/http/controllers/Entry/Api'
        )

        append_web_routes(
            os.path.join(package_directory,
                         '../entry_snippets/routes/EntryRoutes.py')
        )
