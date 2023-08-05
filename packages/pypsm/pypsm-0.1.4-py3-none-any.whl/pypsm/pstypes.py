class PSType(object):
    """A powershell type"""
    def __init__(self, psname, typ):
        self._type = typ
        self.name = psname

    def __call__(self, value):
        return self._type(value)

    def __str__(self):
        return 'PSType(name=%s, type=%s)' % (self.name, self._type)

    def __repr__(self):
        return self.__str__()




psstring = PSType('string', str)
psint = PSType('int', int)
psbool = PSType('bool', bool)
psarray = PSType('Object[]', list)
psswitch = PSType('switch', lambda v: v['IsPresent'])
