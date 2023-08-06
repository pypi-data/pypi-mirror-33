import os
from docker_emperor.command import Command
import docker_emperor.logger as logger

'''
or docker-machine ssh virtualbox -- tce-load -wi rsync
'''
def run(root, *args, **kwargs):

    machine_status = root.machine.status
    if machine_status == 'Stopped':
        root.machine.start()

    if machine_status == 'Running':

        # docker-machine mount dev:/home/docker/foo foo
        # Command(
        #     root.machine.path,
        #     'mount',
        #     '-u',
        #     '{}:{}'.format(
        #         root.machine.name, 
        #         os.path.join('/home/docker/', root.compose.project_path, 'edoc')
        #     ),
        #     'edoc', 
        #     sys=True
        # )
    
        Command(
            root.compose.path,
            'down',
            '--remove-orphans',
            env=root.machine.docker_env,
            sys=True
        )

        Command(
            root.compose.path,
            '--project-directory=.',
            'up',
            env=root.machine.docker_env,
            sys=True
        )