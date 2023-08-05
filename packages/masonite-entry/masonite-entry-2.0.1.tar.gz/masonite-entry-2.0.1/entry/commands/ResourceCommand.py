import os
from cleo import Command


package_directory = os.path.dirname(os.path.realpath(__file__))


class ResourceCommand(Command):
    """
    Creates a new API resource

    entry:resource
        {name : Name of the resource you want to create}
    """

    def handle(self):
        resource = self.argument('name')
        if not os.path.isfile('app/http/resources/{0}.py'.format(resource)):
            if not os.path.exists(os.path.dirname('app/http/resources/{0}.py'.format(resource))):
                # Create the path to the resource if it does not exist
                os.makedirs(os.path.dirname('app/http/resources/{0}.py'.format(resource)))

            f = open('app/http/resources/{0}.py'.format(resource), 'w+')

            f.write("''' A {0} API Resource '''\n".format(resource))
            f.write('from entry.api.Resource import Resource\n')
            f.write('from entry.api.JsonSerialize import JsonSerialize\n\n\n')
            f.write("class {0}(Resource, JsonSerialize):\n    model = None\n".format(resource))
            f.close()
            self.info('Resource Created Successfully!')
        else:
            self.error('Resource Already Exists!')
