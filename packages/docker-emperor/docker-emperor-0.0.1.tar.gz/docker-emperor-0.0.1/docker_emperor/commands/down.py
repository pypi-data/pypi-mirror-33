import os
from docker_emperor.commands import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):

    Command(
        root.compose.path,
        'down',
        '--remove-orphans',
        sys=True,
    )