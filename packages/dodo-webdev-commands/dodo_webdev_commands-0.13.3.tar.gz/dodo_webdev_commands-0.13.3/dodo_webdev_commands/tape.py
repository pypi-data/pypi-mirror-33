from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo
import os
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = ArgumentParser()
    parser.add_argument('tape_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    args.webpack = Dodo.get_config("/WEBPACK/webpack", "webpack")
    args.webpack_config = Dodo.get_config("/TAPE/webpack_config")
    args.tape = Dodo.get_config("/TAPE/tape"),
    args.bundle_file = Dodo.get_config("/TAPE/bundle_file"),
    return args


if Dodo.is_main(__name__):
    args = _args()

    Dodo.runcmd(
        [args.webpack, "--config", args.webpack_config],
        cwd=os.path.dirname(args.webpack_config))
    Dodo.runcmd([
        args.tape,
        args.bundle_file,
    ] + remove_trailing_dashes(args.tape_args))
