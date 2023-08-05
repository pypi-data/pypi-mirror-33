import argparse
from .run import App


def run(args):
    App.run(args.config)


def prepare(args):
    App.prepare()


arg_parser = argparse.ArgumentParser(
    description='A MySQL csv import tool')

sub_parsers = arg_parser.add_subparsers(help='sub-command help')

run_parser = sub_parsers.add_parser('run', help='run help')
run_parser.set_defaults(func=run)
run_parser.add_argument('-c', '--config',
                        default=App.DEFAULT_CONFIG_FILE,
                        help='Configuration file')

prepare_parser = sub_parsers.add_parser('prepare', help='prepare help')
prepare_parser.set_defaults(func=prepare)

args = arg_parser.parse_args()

if 'func' in args:
    args.func(args)
else:
    arg_parser.parse_args(['--help'])
