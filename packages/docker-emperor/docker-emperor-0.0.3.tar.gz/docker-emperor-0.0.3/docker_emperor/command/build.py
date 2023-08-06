from docker_emperor.command import Command


def run(root, *args):

    machine_status = root.machine.status
    if machine_status == 'Stopped':
        root.machine.start()

    if machine_status == 'Running':
        root.compose.combines()
        Command(
            root.compose.path, 
            'build',
            *args, 
            env=root.machine.docker_env,
            sys=True
        )