import os
from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):


    # Command(
    #     root.machine.path,
    #     'mount',
    #     '{}:{}'.format(
    #         root.machine.name, 
    #         os.path.join('/home/docker/', root.compose.project_path)
    #     ),
    #     '.', 
    # )
    
    Command(
        root.compose.path,
        '--project-directory=.',
        'up',
        env=root.machine.docker_env,
        sys=True
    )