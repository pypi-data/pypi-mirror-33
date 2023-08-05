import argparse
import json
import os.path
import base64
import inspect
from functools import wraps

from .psargument import PSArgument
from .psfunction import PSFunction


FUNC_TEMPLATE = """
function {name} {{
    param({param})
    $params = ConvertTo-Json $PsBoundParameters
    $paramsbytes = [System.Text.Encoding]::UTF8.GetBytes($params)
    $paramsb64 = [Convert]::ToBase64String($paramsbytes)
    $python = Python3\\Get-Python3EXE

    & $python "$PSScriptRoot\\{file}" --invoke {name} $paramsb64
}}
"""


class PSModule(object):
    def __init__(self, file, pythonpath='pymodules'):
        self.file = file
        self._funcs = {}
        self.pythonpath = pythonpath


    def addfunc(self, psfunction):
        self._funcs[psfunction.name] = psfunction


    def __call__(self, args=None):
        """
            The main entry point of the psmodule
            :param args: Args is an object (like a Namespace from Argparse)
            that contains
                invoke = (function_name, arguments_json)
            or
                psm = Path/to/Module.psm1

            if args is not specified, it will be parsed from sys.argv by
            argparse, if psm and invoke are specified, psm will be ignored
        """
        if args is None:
            pars = argparse.ArgumentParser()
            pars.add_argument('--invoke', nargs=2)
            pars.add_argument('--psm')
            args = pars.parse_args()
        
        if args.invoke:
            name, args_jsonb64 = args.invoke
            self._funcs[name].invoke(json.loads(base64.b64decode(args_jsonb64)))

        elif args.psm:
            self.savepsm(args.psm)

        
    def getpsm(self):
        file = ['#Requires -Version 3',
                '$ENV:PYTHONPATH = "$PSScriptRoot\\{}"'.format(self.pythonpath)]
        for i in self._funcs.values():
            file.append(self._psm_function(i))
        return '\n'.join(file)


    def savepsm(self, file):
        """Save this module as powershell module definition"""
        with open(file, 'w') as fp:
            fp.write(self.getpsm())


    def _psm_function(self, psfunc):
        """
            Get a powershell function (definition and body)
            based on a PSFunction object
        """
        param = ['[{}]${}'.format(i.type.name, i.name)
                 for i in psfunc.args.values()]
        return FUNC_TEMPLATE.format(name=psfunc.name,
                                    param=','.join(param),
                                    file=os.path.basename(self.file))


    @staticmethod
    def _get_psname(name):
        return '-'.join([i.capitalize() for i in name.split('_')])

    
    def function(self, f):
        """Add a function with decorators"""
        sig = inspect.signature(f)
        args = []

        for name, param in sig.parameters.items():
            default = (None if param.default == inspect.Parameter.empty
                       else param.default)
            required = param.default == inspect.Parameter.empty

            args.append(PSArgument(name, param.annotation,
                                   default=default, required=required))

        func = PSFunction(self._get_psname(f.__name__), f, *args)
        self.addfunc(func)
        return f
