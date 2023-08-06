import six
import os
from docker_emperor.commands import Command
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
        self.path = path
        self.name = '{}.{}'.format(self.machine.name, self.context.name)    
        self.project_name = self.data.pop(
            'project_name',  
            os.environ.get('COMPOSE_PROJECT_NAME', 
                os.path.basename(self.root.root_path)
            )
        )
        self.project_path = '{}.{}'.format(self.project_name, self.name)

    @memoized_property
    def data(self): return dict(self.root.data)

    @memoized_property
    def yml(self): 
        self.yml = yamp_dump(self.data)
        for name, value in self.environment:
            self.yml = self.yml.replace('${{{}}}'.format(name), value)
        return self.yml

    def combines(self): 
        self.environment < self.context.environment < self.machine.environment 
        self.project_name = self.environment.get('COMPOSE_PROJECT_NAME', self.project_name)
        self.services < self.context.services < self.machine.services 
        for service in self.services:
            service.environment < self.environment
            service['container_name'] = service.get('container_name', '{}.{}'.format(self.project_path, service.name))
            if not 'image' in service and not 'build' in service:
                service['image'] = service.name
            if 'image' in service:
                if os.path.isfile(os.path.join(self.root.root_path, service['image'], 'Dockerfile')):
                    service['build'] = service['image']

    @memoized_property
    def filename(self): 
        filename = os.path.join(self.root.root_path, 'docker-compose.{}.yml'.format(self.project_path))
        file = open(filename, 'wb')# = tempfile.NamedTemporaryFile(mode='w+b', bufsize=-1, suffix='.yml', prefix='docker-compose-', dir=None, delete=False)
        file.write(self.yml)
        file.close()
        return filename


    @classmethod
    def has_command(cls, name):
        return hasattr(cls, 'command_{}'.format(name))

    def run_command(self, name, *args):
        if Compose.has_command(name):
            getattr(self, 'command_{}'.format(name))(*args)


    def command_build(self, *args): 
        self.combines()
        self._run('build')

    def command_deploy(self, *args):
        target = ' docker@{}:{}'.format(self.machine.ip, os.path.join('/home/docker/', self.project_path))
        print(target)
        return Command(
            'rsync',
            '-rv --exclude ".git"',
            '--exclude ".svn"',
            '.', 
            target,
            sys=True,
            log=True
        )

    def command_run(self, *args): 
        self.combines()
        self._run('down', "--remove-orphans")
        self._run('up', *args)

    def command_rund(self, *args): 
        self.command_run('-d', *args)

    def command_down(self, *args): 
        self.combines()
        self._run('down', *args)

    def command_up(self, *args): 
        self.combines()
        self._run('up', *args)

    def command_logs(self, *args): 
        self.combines()
        self._run('logs', *args)

    def command_ps(self, *args): 
        self.combines()
        self._run('ps', *args)


    # def compose(self, *args):
    #     fn = self.context.compose_filename.replace(self.root ,'')

    #     cmd = ['docker-compose', '-f', '{} {}'.format(self.compose_filename)] + list(args)
    #     self._run(cmd)



    # @property
    # def data(self):
    #     if not hasattr(self, '_data'):

    #         data = {}

            # self.service = self.machine.merge(self.machine, self.machine)

            # data = combine(self.context.data, self.de.data)
            # self.environment = combine(self.data.pop('environment', {}), self.root.get('environment', {}), as_varlist=True)
            # self.compose_file = None
            # self.yml = ''

            # self.project_name = self.root.pop(
            #     'project_name', 
            #     self.environment.get('COMPOSE_PROJECT_NAME') if isinstance(self.environment, dict) else None
            # )
            # if not self.project_name:
            #     os.environ.get('COMPOSE_PROJECT_NAME', 'unknow')

            # self.shortcuts = combine(self.data.pop('shortcuts', {}), self.root.get('shortcuts', {}))

            # self.version = self.data.get('version', self.root.get('version', '3.3'))
            # self.data = apply_shortcuts(self.data, self.shortcuts)
            # if not 'version' in data:
            #     data['version'] = self.version
            
        #     setattr(self, '_data', data)
        # return getattr(self, '_data') 

    # def combine_services(self):

    #     for name, service in self.data.get('services', {}).items():
    #         if service:
    #             service['environment'] = combine(service.get('environment'), self.environment, as_varlist=True)
    #             service['container_name'] = service.get('container_name', '{}.{}.{}'.format(self.project_name, self.name, name))
    #             if not 'image' in service and not 'build' in service:
    #                 service['image'] = name
    #             if 'image' in service:
    #                 if os.path.isdir(service['image']):
    #                     service['build'] = service['image']

    # @property
    # def compose_filename(self):

    #     if not hasattr(self, '_yml'):

    #         self.data.pop('shortcuts', {})

    #         self.yml = yaml.dump(self.data, Dumper=YamlDumper, default_flow_style=False, indent=4)
    #         for name, value in varlist_to_dict(self.environment).items():
    #             self.yml = self.yml.replace('${{{}}}'.format(name), value)

    #         self.compose_filename = os.path.join(self.de.root, 'docker-compose.{}.{}.yml'.format(self.project_name, self.name))
    #         self.compose_file = open(self.compose_filename, 'wb')# = tempfile.NamedTemporaryFile(mode='w+b', bufsize=-1, suffix='.yml', prefix='docker-compose-', dir=None, delete=False)
    #         self.compose_file.write(self.yml)
    #         self.compose_file.close()

    #         setattr(self, '_yml')

    #     return getattr(self, '_yml')
