import six
import os
from docker_emperor.command import Command
from docker_emperor.nodes import HasEnvironment, HasContexts, HasMachines, HasServices
from docker_emperor.utils import combine, memoized_property, yamp_dump


__all__ = ['Compose']

''' 
Compose stack
Context + Machine
'''

class Compose(HasEnvironment, HasServices):


    def __init__(self, root, path="docker-compose"):

        self.root = root
        self.context = root.context
        self.machine = root.machine
        self.name = '{}.{}'.format(self.machine.name, self.context.name)    
        self.project_name = self.data.pop(
            'project_name',  
            os.environ.get('COMPOSE_PROJECT_NAME', 
                os.path.basename(self.root.root_path)
            )
        )
        self.project_path = '{}.{}'.format(self.project_name, self.name)
        #self.filename = os.path.join(self.root.root_path, self.project_path, 'docker-compose.yml')
        self.filename = os.path.join(self.root.root_path, 'docker-compose.{}.yml'.format(self.project_path))
         #self.path = "{} -f {}".format(path, self.filename)
        self.path = "{} -f {}".format(path, self.filename)
        self.combines()


    def combines(self): 
        self.environment < self.context.environment < self.machine.environment 
        self.project_name = self.environment.get('COMPOSE_PROJECT_NAME', self.project_name)
        self.services < self.context.services < self.machine.services 
        for service in self.services:
            service.environment < self.environment
            service['container_name'] = service.get('container_name', '{}.{}.{}'.format(self.project_name, self.name, service.name))
            if not 'image' in service and not 'build' in service:
                service['image'] = service.name
            if 'image' in service:
                if os.path.isfile(os.path.join(self.root.root_path, service['image'], 'Dockerfile')):
                    service['build'] = service['image']
        file = open(self.filename, 'wb')# = tempfile.NamedTemporaryFile(mode='w+b', bufsize=-1, suffix='.yml', prefix='docker-compose-', dir=None, delete=False)
        file.write(self.yml)
        file.close()

    @memoized_property
    def data(self): return dict(self.root.data)

    @memoized_property
    def yml(self): 
        self.yml = yamp_dump(self.data)
        for name, value in self.environment:
            self.yml = self.yml.replace('${{{}}}'.format(name), value)
        return self.yml

