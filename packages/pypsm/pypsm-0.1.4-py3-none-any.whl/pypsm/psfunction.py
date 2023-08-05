import sys


class PSFunction(object):
    """A powershell function / cmdlet"""
    def __init__(self, name, func, *args, doc=None):
        self.name = name
        self.args = {i.name: i for i in args}
        self._func = func
        self.doc = '' if doc is None else doc

    def _parse_args(self, values):
        result = {}
        for name, arg in self.args.items():
            result[name] = arg(values.pop(name, None))
        if values:
            raise ValueError(
                'Invalid arguments %s' % '.'.join(values.keys()))
        return result

    def invoke(self, args):
        try:
            args = self._parse_args(args)
        except TypeError as e:
            self.help(str(e))
            exit(1)
        self._func(**args)


    def help(self, message):
        """Print help"""
        args = ['-{0} {0}'.format(i.name)
                for i in self.args.values() if i.required]
        optargs = ['[-{0} {0}]'.format(i.name)
                   for i in self.args.values() if not i.required]

        print('Useage: {} {} {}\nError: {}'
              .format(self.name, ', '.join(args),
                      ', '.join(optargs), message), file=sys.stderr)
