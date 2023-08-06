import os
import sys
import yaml
import tempfile
import collections
import six
import argparse
import subprocess
import imp
from pprint import pprint
from docker_emperor.nodes import HasEnvironment, HasContexts, HasMachines, HasServices
from docker_emperor.compose import Compose
from docker_emperor.command import Command
from docker_emperor.utils import memoized_property, combine, yamp_load
from docker_emperor.version import __version__
import docker_emperor.logger as logger


class DockerWorkonException(Exception):
    pass

# version, services, networks, volumes, secrets, configs, and extensions starting with "x-"


class DockerWorkon(HasEnvironment, HasServices, HasContexts, HasMachines):

    version = "{}".format(__version__)

    def __init__(self):

        self.module_root = os.path.dirname(os.path.abspath(__file__))
        self.root_path = os.getcwd()
        self.compose = None
        self.context = None
        self.machine = None 

    def entrypoint(self, action=None, *args):
        try:
            args = list(args)
            # logger.info(action, args)

            if action:

                if u'@' in action:
                    context_machine = action.split(u'@', 2)
                    self.context = self.contexts.select(context_machine[0])
                    self.machine = self.machines.select(context_machine[-1])
                    if len(args):
                        action = args[0]
                        args = args[1:]
                    else:
                        action = None
                else:
                    self.context = self.contexts.default
                    self.machine = self.machines.default

                self.compose = Compose(self)                                
                self.run_command(action, *args)

            else:
                logger.info('docker-workon version {}'.format(self.version))

        except DockerWorkonException as e:
            logger.error(e)


    def run_command(self, name, *args):

        if '--verbose' in args:
            Command.verbose = 1

        try:
            mod = __import__('docker_emperor.command.{}'.format(name), globals(), locals(), ['run'], 0)
            mod.run(self, *args)
        except ImportError as e:
            logger.error('Unknown command {}'.format(name))
        # if hasattr(self, cmd_method):
        #     getattr(self, cmd_method)(*args, **kwargs)

    @memoized_property
    def data(self):
        for file in ['docker-emperor.yml', 'docker-compose.yml']:
            filename = os.path.join(self.root_path, file)
            if os.path.isfile(filename):
                data = yamp_load(open(filename, 'rb').read())
                if not isinstance(data, dict):
                    raise DockerWorkonException('{} is not yml as dict'.format(os.path.basename(file)))
                return data
        raise DockerWorkonException('{} not found in {}'.format(os.path.basename(file), self.root_path))


dw = DockerWorkon()

def entrypoint():
    argsparser = argparse.ArgumentParser(description='Docker web apps composer')
    argsparser.add_argument('args', nargs=argparse.REMAINDER, action="store")    
    dw.entrypoint(*argsparser.parse_args().args)

if __name__ == "__main__": entrypoint()










# # @property
# # def machine(self):
# #     attr = '_machine'
# #     if not hasattr(self, attr): setattr(self, attr, self.machines.select(self.machine_name))
# #     return getattr(self, attr)


# def _run(self, *args):
#     return Command(self, self.compose_path, *args, env=self.machine.docker_env)


# def cmd_start(self, *args):
#     self.cmd_prune()
#     self.compose("down --remove-orphans")
#     self.compose("up", *args)

# def cmd_startd(self, *args):
#     self.cmd_start('-d', *args)

# def cmd_logs(self, *args):
#     self.compose('logs', '-f', *args)


# def cmd_run(self, *args):
#     self.compose('run', *args)

# def cmd_exec(self, *args):
#     self.compose('exec', *args)

# def cmd_sethost(self, host):
#     bin_path = os.path.join(self.module_root, 'bin')
#     self.cmd("docker run -t -i -v {bin_path}/sethost:/bin/sethost -v /etc/hosts:/etc/hosthosts -v /etc/hosts.bak:/etc/hosthosts.bak busybox sh /bin/sethost 0.0.0.0 {}".format(host))

# def cmd_prune(self):
#     self.cmd("docker network prune -f")
#     self.cmd("docker system prune -f")
#     self.cmd("docker volume prune -f")


# def cmd(self, *args):
#     cmd = " ".join(args).strip()
#     self.log_info('> {}'.format(cmd))
#     try:
#         output = subprocess.check_output(cmd.split())
#         print(output.strip())
#     except Exception as e:
#         raise DockerWorkonException()#"error: " + str(e))#, sys.exc_info())


# def log_info(self, message):
#     print('{}{}{}{}'.format(C.YELLOW, C.LYELLOW, message, C.ENDC))

# def log_success(self, message):
#     print('{}{}{}{}'.format(C.GREEN, C.LGREEN, message, C.ENDC))

# def log_error(self, message):
#     print('{}{}{}{}'.format(C.ERROR, C.LERROR, message, C.ENDC))


