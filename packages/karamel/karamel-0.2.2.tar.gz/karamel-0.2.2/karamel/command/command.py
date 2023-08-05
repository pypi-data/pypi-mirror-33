import argparse

class Command:

    def __init__(self, command_name, description):
        self.parser = argparse.ArgumentParser(prog=command_name, description=description, add_help=False)
        self.parser.set_defaults(callback=self)
        self.subparsers = None

    def run(self):
        args = self.parser.parse_args()
        args.callback(args)

    def add_command(self, command, description='', help=''):
        if self.subparsers == None:
            self.subparsers = self.parser.add_subparsers(help=help)
        subparser = self.subparsers.add_parser(command.parser.prog, help=command.parser.description)
        subparser.__dict__ = command.parser.__dict__;

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def callback(self, args):
        pass

    def __call__(self, args):
        self.callback(args)
