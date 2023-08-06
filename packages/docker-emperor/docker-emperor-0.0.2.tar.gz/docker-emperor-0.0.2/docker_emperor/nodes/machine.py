import six
from docker_emperor.command import Command
from docker_emperor.nodes import HasEnvironment, HasServices
from docker_emperor.utils import combine, memoized_property, memoized
import docker_emperor.logger as logger


__all__ = ['HasMachines', 'Machines', 'Machine']


# DRIVERS

# Amazon Web Services
# Microsoft Azure
# Digital Ocean
# Exoscale
# Google Compute Engine
# Generic
# Microsoft Hyper-V
# OpenStack
# Rackspace
# IBM Softlayer
# Oracle VirtualBox
# VMware vCloud Air
# VMware Fusion
# VMware vSphere
# VMware Workstation (unofficial plugin, not supported by Docker)
# Grid 5000 (unofficial plugin, not supported by Docker)


class HasMachines():
    
    @property
    def machines(self):
        attr = '_machines'
        if not hasattr(self, attr): setattr(self, attr, Machines(self.data.pop('machines', {})))
        return getattr(self, attr)


class Machines():

    def __init__(self, data):
        self.data = data
        if not isinstance(self.data, dict): self.data = {}

    @memoized
    def select(self, name='default', default_data=None):
        data = self.data.get(name, default_data)
        if isinstance(data, six.string_types):
            name = data
            data = self.data.get(name)
        return Machine(name, data)

    @property
    def default(self): 
        return self.select('default', default_data={})
    
    @property
    def all(self): 
        return { name: Machine(name, data) for name, data in self.data.items() }


class Machine(HasEnvironment, HasServices):

    COMMANDS = [
        'ssh'
    ]

    def __init__(self, name, data, path="docker-machine"):

        self.key = name
        self.name = name
        self.data = data
        if not isinstance(self.data, dict): self.data = {}
        self.path = path

        # SET DRIVER
        self.driver = self.data.get('driver')
        if not isinstance(self.driver, six.string_types): self.driver = 'generic --generic-ip-address localhost'

        # SET HOSTS
        self.hosts = self.data.get('hosts')
        if not isinstance(self.hosts, list): self.hosts = []

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)



    @property
    def exists(self):
        cmd = self._run("ls", "--filter", "NAME=" + self.name, "--format", "{{.Name}}", env=self.docker_env, tty=False)
        for line in cmd.lines:
            if line == self.name:return True
        return False

    def command_ssh(self, *args, **kwargs):
        self._run('ssh', self.name, *args, **kwargs)

    def command_active(self, *args, **kwargs):
        self._run('active', *args, env=self.docker_env, **kwargs)

    def command_exists(self, *args, **kwargs):
        logger.warning(('Machine {} exists' if self.exists else 'Machine {} doesn\'t exists, execute: dw create').format(self.name))


    @memoized_property
    def docker_env(self):
        cmd = Command(
            self.path, 
            'env', 
            self.name, 
            log=True
        )
        starts = 'export '
        return [line.lstrip(starts) for line in cmd.lines if line.startswith(starts)]


    @property
    def start(self):
        Command(self.path, 'start', self.name, sys=True).log()    

    @property
    def status(self):
        return Command(self.path, 'status', self.name).out
    
    @property
    def ip(self):
        return Command(self.path, 'ip', self.name, log=False, env=self.docker_env).out.strip()

    @property
    def pwd(self):
        return Command(self.path, 'ssh', self.name, 'pwd', log=False, env=self.docker_env).out.strip()

    @property
    def inspect(self):
        cmd = self._run('inspect', self.name, env=self.docker_env, tty=False)
        return cmd.out

    @property
    def active(self):
        cmd = self._run('active', env=self.docker_env, tty=False)
        return cmd.out

    def remove(self):
        cmd = self._run('rm', self.name, env=self.docker_env)
        return cmd

# active
# config
# create
# env
# help
# inspect
# ip
# kill
# ls
# mount
# provision
# regenerate-certs
# restart
# rm
# scp
# ssh
# start
# stop
# upgrade
# url