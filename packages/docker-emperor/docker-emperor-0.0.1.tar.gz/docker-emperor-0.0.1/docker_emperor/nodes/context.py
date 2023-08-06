import six
from docker_emperor.nodes import HasEnvironment, HasServices
from docker_emperor.utils import combine, memoized_property, memoized


__all__ = ['HasContexts', 'Contexts', 'Context']


class HasContexts():
    
    @property
    def contexts(self):
        attr = '_contexts'
        if not hasattr(self, attr): 
            setattr(self, attr, Contexts(self.data.pop('contexts', {})))
        return getattr(self, attr)


class Contexts():

    def __init__(self, data):
        self.data = data
        if not isinstance(self.data, dict): self.data = {}

    @memoized
    def select(self, name='default', default_data=None): 
        data = self.data.get(name, default_data)
        if isinstance(data, six.string_types):
            name = data
            data = self.data.get(name)
        return Context(name, data)

    @property
    def default(self): 
        return self.select('default', default_data={})
    
    @property
    def all(self): 
        return { name: Context(name, data) for name, data in self.data.items() }


class Context(HasEnvironment, HasServices):

    COMMANDS = [
    ]


    def __init__(self, name, data):

        self.name = name
        self.data = data

    @classmethod
    def has_command(cls, name):
        return hasattr(cls, 'command_{}'.format(name))

    def run_command(self, name, *args):
        if Context.has_command(name):
            getattr(self, 'command_{}'.format(name))(*args)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)


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

    #         self.compose_filename = os.path.join(self.root.root, 'docker-compose.{}.{}.yml'.format(self.project_name, self.name))
    #         self.compose_file = open(self.compose_filename, 'wb')# = tempfile.NamedTemporaryFile(mode='w+b', bufsize=-1, suffix='.yml', prefix='docker-compose-', dir=None, delete=False)
    #         self.compose_file.write(self.yml)
    #         self.compose_file.close()

    #         setattr(self, '_yml')

    #     return getattr(self, '_yml')
