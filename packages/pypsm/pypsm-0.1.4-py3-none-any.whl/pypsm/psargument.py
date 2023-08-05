
class PSArgument(object):
    """An Argument to a PSFunction"""
    def __init__(self, name, pstype, default=None, required=None):
        self.name = name
        self.type = pstype
        self.default = default
        if required is None:
            self.required = default is None
        else:
            self.required = required

    def __str__(self):
        return ('PSArgument(name=%s, type=%s, required=%s'
                % (self.name, self.type, self.required))

    def __repr__(self):
        return self.__str__()


    def __call__(self, value):
        if self.required and value is None:
            raise TypeError('Argument %s is required' % self.name)

        if value is not None:
            return self.type(value)

        if callable(self.default): # Allow default to be callable
            return self.default()

        return self.default
