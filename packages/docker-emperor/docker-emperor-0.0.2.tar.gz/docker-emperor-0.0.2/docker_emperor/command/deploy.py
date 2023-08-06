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


        # ex. docker-machine scp -r -d . virtualbox:/home/docker/project.dev.localhost/

        Command(
            root.machine.path,
            'scp',
            '-r',
            '-d',
            '.', 
            '{}:{}'.format(
                root.machine.name, 
                os.path.join('/home/docker/', root.compose.project_path)
            ),
            sys=True,
            log=True
        )

        root.run_command('build')
        root.run_command('start')