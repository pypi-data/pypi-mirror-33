import os
from docker_emperor.command import Command
import docker_emperor.logger as logger


def run(root, *args, **kwargs):

    machine_status = root.machine.status
    if machine_status == 'Stopped':
        root.machine.start()

    if machine_status == 'Running':

        root.run_command('down')
        root.run_command('up')