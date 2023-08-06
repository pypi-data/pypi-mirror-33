from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):
    
    Command(
        root.machine.path, 
        'create', 
        '--driver',
        root.machine.driver,        
        root.machine.name,
        *args,
        sys=True
    )