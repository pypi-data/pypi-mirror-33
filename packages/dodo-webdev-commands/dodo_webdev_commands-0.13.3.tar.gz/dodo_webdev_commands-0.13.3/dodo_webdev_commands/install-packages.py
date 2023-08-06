from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import os


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.node_modules_dir = Dodo.get_config('/SERVER/node_modules_dir')
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    pip = os.path.join(Dodo.get_config('/SERVER/venv_dir'), 'bin', 'pip')
    requirements_filename = Dodo.get_config('/SERVER/pip_requirements')

    Dodo.runcmd([pip, 'install', '-r', requirements_filename])
    Dodo.runcmd(
        ['yarn', 'install'],
        cwd=os.path.abspath(os.path.join(args.node_modules_dir, '..')))
