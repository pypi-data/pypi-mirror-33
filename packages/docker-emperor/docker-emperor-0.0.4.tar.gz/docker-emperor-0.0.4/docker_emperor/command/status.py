from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):
    
    status = Command(
        root.machine.path, 
        'status', 
        root.machine.name
    ).out

    logger.warning(status)