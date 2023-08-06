from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):
    
    Command(
        root.machine.path, 
        'ssh', 
        root.machine.name,
        *args,
        sys=True
    )