from .module import Module


class Delivery(Module):
    dependencies = ['service']

    def __init__(self, **kwargs):
        super().__init__('delivery', **kwargs)

    def add_arguments(self, parser):
        subp = parser.add_subparsers(help='delivery help')

        p = subp.add_parser('mk', help='add delivery project')
        p.add_argument('name', metavar='NAME', help='project name')
        p.set_defaults(delivery_handler=self.handle_make)

    def handle_make(self, args):
        self.make(args.name)

    def make(self, name):
        pass
