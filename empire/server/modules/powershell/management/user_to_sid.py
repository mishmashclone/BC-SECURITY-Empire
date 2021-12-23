from __future__ import print_function

import pathlib
from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        
        script = "(New-Object System.Security.Principal.NTAccount(\"%s\",\"%s\")).Translate([System.Security.Principal.SecurityIdentifier]).Value" %(params['Domain'], params['User'])
   
        if main_menu.obfuscate:
            script = data_util.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=main_menu.obfuscateCommand)
        script = data_util.keyword_obfuscation(script)

        return script
