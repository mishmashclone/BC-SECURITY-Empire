from __future__ import print_function

import pathlib
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
        module_source = main_menu.installPath + "/data/module_source/situational_awareness/host/Invoke-Seatbelt.ps1"
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
            script = data_util.obfuscate(installPath=main_menu.installPath, psScript=module_code,
                                         obfuscationCommand=main_menu.obfuscateCommand)
        else:
            script = module_code
        script_end = 'Invoke-Seatbelt -Command "'

        # Add any arguments to the end execution of the script
        if params['Command']:
            script_end += " " + str(params['Command'])
        if params['Group']:
            script_end += " -group=" + str(params['Group'])
        if params['Computername']:
            script_end += " -computername=" + str(params['Computername'])
        if params['Username']:
            script_end += " -username=" + str(params['Username'])
        if params['Password']:
            script_end += " -password=" + str(params['Password'])
        if params['Full'].lower() == 'true':
            script_end += " -full"
        if params['Quiet'].lower() == 'true':
            script_end += " -q"

        script_end = script_end.replace('" ', '"')
        script_end += '"'

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
