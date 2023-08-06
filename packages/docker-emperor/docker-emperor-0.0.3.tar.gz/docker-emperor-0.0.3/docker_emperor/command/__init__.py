import six
import os
import subprocess
import docker_emperor.logger as logger


__all__ = ['Command']

COMPOSE_COMMANDS = [
    'build',
    'bundle',
    'config',
    'create',
    'down',
    'events',
    'exec',
    'help',
    'kill',
    'logs',
    'pause',
    'port',
    'ps',
    'pull',
    'push',
    'restart',
    'rm',
    'run',
    'scale',
    'start',
    'stop',
    'top',
    'unpause',
    'up',
]

MACHINE_COMMANDS = [
    'active',
    'config',
    'create',
    'env',
    'help',
    'inspect',
    'ip',
    'kill',
    'ls',
    'mount',
    'provision',
    'regenerate-certs',
    'restart',
    'rm',
    'scp',
    'ssh',
    'start',
    'status',
    'stop',
    'upgrade',
    'url',
]



class Command():

    verbose = 0

    def __repr__(self):
        return self.cmd_line

    def __init__(self, *args, **kwargs):

        self.cmd = list(args)
        self.error = None

        for i, arg in enumerate(self.cmd):
            if isinstance(arg, six.integer_types):
                self.cmd[i] = str(arg)
            elif not isinstance(arg, six.string_types):
                raise Exception("Argument {} is invalid: {} is not string types".format(i, arg))

        # if kwargs.get('log', True):
        #     logger.info(" ".join(self.cmd))

        self.env = kwargs.pop('env', [])
        if not self.env: self.env = []
        if not isinstance(self.env, list):
            raise Exception("Env arguments are invalid: {} is not list types".format(self.env))       

        self.cmd_line = " ".join(self.env + self.cmd)

        if self.verbose >= 1:
            logger.comment(" ".join(self.env + self.cmd))

        # if kwargs.get('log', True):
        #     logger.comment("Env.\n" + "\n".join(self.env))

        if kwargs.get('sys', False):
            self.out = os.system(" ".join(self.env + self.cmd))

        else:
            self.lines = []
            self.process = subprocess.Popen(
                " ".join(self.env + self.cmd), 
                shell=True, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            self.out = ''

            for line in iter(self.process.stdout.readline, ''):  # replace '' with b'' for Python 3
                self.out += line
                self.lines.append(line.strip())
                self.last_line = line

            self.out = self.out.strip()
            stdout, stderr = self.process.communicate()
            self.error_code = self.process.returncode
            self.error = stderr.decode('utf-8').strip()


        if self.error:                
            self.error = self.error.replace('docker-machine ls', 'dw ls')
            if not kwargs.get('silently_fail', False):
                logger.error(self.error)
                exit(0) 

    def log(self):
        logger.success(self.out)


    # def _run(self, cmd, raise_error=True):
    #     """
    #     Run a docker-machine command, optionally raise error if error code != 0
    #     Args:
    #         cmd (List[str]): a list of the docker-machine command with the arguments to run
    #         raise_error (bool): raise an exception on non 0 return code
    #     Returns:
    #         tuple: stdout, stderr, error_code
    #     """
    #     cmd = [self.machine_path] + cmd
    #     print(" ".join(cmd))

    #     # output = subprocess.check_output(cmd)
    #     # print(output.strip())
    #     # return output

    #     process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     for line in iter(process.stdout.readline, ''):  # replace '' with b'' for Python 3
    #         print(line.strip())

    #     stdout, stderr = process.communicate()
    #     # print(stdout, stderr)
    #     error_code = process.returncode
    #     # if raise_error and error_code:
    #     #     raise RuntimeError("cmd returned error %s: %s" % (error_code, stderr.decode('utf-8').strip()))
    #     return stdout.decode('utf-8'), stderr.decode('utf-8'), error_code


    # def _run_blocking(self, cmd, raise_error=True):
    #     """
    #     Run a docker-machine command, optionally raise error if error code != 0
    #     Args:
    #         cmd (List[str]): a list of the docker-machine command with the arguments to run
    #         raise_error (bool): raise an exception on non 0 return code
    #     Returns:
    #         tuple: stdout, stderr, error_code
    #     """
    #     cmd = [self.machine_path] + cmd

    #     # output = subprocess.check_output(cmd)
    #     # print(output.strip())
    #     # return output


    #     p = subprocess.open(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     stdout, stderr = p.communicate()
    #     error_code = p.wait()

    #     # if raise_error and error_code:
    #     #     raise RuntimeError("cmd returned error %s: %s" % (error_code, stderr.decode('utf-8').strip()))
    #     return stdout.decode('utf-8'), stderr.decode('utf-8'), error_code