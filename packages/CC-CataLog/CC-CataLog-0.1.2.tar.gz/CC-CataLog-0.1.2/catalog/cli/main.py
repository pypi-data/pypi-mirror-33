import argparse
import sys

from catalog import __version__
from importlib import import_module # type: ignore


commands = [
    ('gui', 'catalog.cli.gui')]

def main(prog ='catalog', description='catalog command line tool',
         version=__version__, commands=commands, hook=None, args=None):
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('--version', action='version',
                        version='%(prog)s-{}'.format(version))
    parser.add_argument('-T', '--traceback', action='store_true')
    subparsers = parser.add_subparsers(title='Sub-commands',
                                       dest='command')

    subparser = subparsers.add_parser('help',
                                      description='Help',
                                      help='Help for sub-command')
    subparser.add_argument('helpcommand', nargs='?')

    functions = {}
    parsers = {}
    for command, module_name in commands:
        cmd = import_module(module_name).CLICommand
        subparser = subparsers.add_parser(
            command,
            help=cmd.short_description,
            description=getattr(cmd, 'description', cmd.short_description))
        cmd.add_arguments(subparser)
        functions[command] = cmd.run
        parsers[command] = subparser

    if hook:
        args = hook(parser, args)
    else:
        args = parser.parse_args(args)

    if args.command == 'help':
        if args.helpcommand is None:
            parser.print_help()
        else:
            parsers[args.helpcommand].print_help()
    elif args.command is None:
        parser.print_usage()
    else:
        f = functions[args.command]
        try:
            if f.__code__.co_argcount == 1:
                f(args)
            else:
                f(args, parsers[args.command])
        except KeyboardInterrupt:
            pass
        except Exception as x:
            if args.traceback:
                raise
            else:
                l1 = '{}: {}\n'.format(x.__class__.__name__, x)
                l2 = ('To get a full traceback, use: {} -T {} ...'
                      .format(prog, args.command))
                parser.error(l1 + l2)
