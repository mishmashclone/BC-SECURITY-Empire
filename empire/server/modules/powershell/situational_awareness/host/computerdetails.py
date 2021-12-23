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
        module_source = main_menu.installPath + "/data/module_source/situational_awareness/host/Get-ComputerDetails.ps1"
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
            script = module_code + "\n\n"

        script_end = ""
        outputf = params.get("OutputFunction", "Out-String")

        for option,values in params.items():
            if option.lower() != "agent" and option.lower() != "outputfunction":
                if values and values != '':
                    if option == "4624":
                        script_end += "$SecurityLog = Get-EventLog -LogName Security; $Filtered4624 = Find-4624Logons $SecurityLog;"
                        script_end += 'Write-Output "Event ID 4624 (Logon):`n";'
                        script_end += "Write-Output $Filtered4624.Values"
                        script_end += f" | {outputf}"
                        script_end = data_util.keyword_obfuscation(script_end)
        for option, values in params.items():
            if option.lower() != "agent" and option.lower() != "outputfunction":
                if values and values != '':
                    if option == "4624":
                        script_end += "$SecurityLog = Get-EventLog -LogName Security; $Filtered4624 = Find-4624Logons $SecurityLog;"
                        script_end += 'Write-Output "Event ID 4624 (Logon):`n";'
                        script_end += "Write-Output $Filtered4624.Values"
                        script_end += f" | {outputf}"
                        if obfuscate:
                            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                                          obfuscationCommand=obfuscation_command)
                        script += script_end
                        return script
                    if option == "4648":
                        script_end += "$SecurityLog = Get-EventLog -LogName Security; $Filtered4648 = Find-4648Logons $SecurityLog;"
                        script_end += 'Write-Output "Event ID 4648 (Explicit Credential Logon):`n";'
                        script_end += "Write-Output $Filtered4648.Values"
                        script_end += f" | {outputf}"
                        if obfuscate:
                            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                                          obfuscationCommand=obfuscation_command)
                        script += script_end
                        return script
                    if option == "AppLocker":
                        script_end += "$AppLockerLogs = Find-AppLockerLogs;"
                        script_end += 'Write-Output "AppLocker Process Starts:`n";'
                        script_end += "Write-Output $AppLockerLogs.Values"
                        script_end += f" | {outputf}"
                        if obfuscate:
                            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                                          obfuscationCommand=obfuscation_command)
                        script += script_end
                        return script
                    if option == "PSLogs":
                        script_end += "$PSLogs = Find-PSScriptsInPSAppLog;"
                        script_end += 'Write-Output "PowerShell Script Executions:`n";'
                        script_end += "Write-Output $PSLogs.Values"
                        script_end += f" | {outputf}"
                        if obfuscate:
                            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                                          obfuscationCommand=obfuscation_command)
                        script += script_end
                        return script
                    if option == "SavedRDP":
                        script_end += "$RdpClientData = Find-RDPClientConnections;"
                        script_end += 'Write-Output "RDP Client Data:`n";'
                        script_end += "Write-Output $RdpClientData.Values"
                        script_end += f" | {outputf}"
                        if obfuscate:
                            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                                          obfuscationCommand=obfuscation_command)
                        script += script_end
                        return script

        # if we get to this point, no switched were specified
        script_end += "Get-ComputerDetails -Limit " + str(params['Limit'])
        if (outputf == "Out-String"):
            script_end += " -ToString | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'
        else:
            script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
