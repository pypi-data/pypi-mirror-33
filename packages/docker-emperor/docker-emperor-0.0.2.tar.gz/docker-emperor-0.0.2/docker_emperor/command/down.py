import os
from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):

    Command(
        root.compose.path,
        'down',
        '--remove-orphans',
        env=root.machine.docker_env,
        sys=True
    )