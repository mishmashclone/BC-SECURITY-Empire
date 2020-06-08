from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-BloodHound',

            'Author': ['@harmj0y', '@_wald0', '@cptjesus', 'rafff'],

            'Description': ('Execute BloodHound data collection (ingestor for version 3).'),

            'Software': '',

            'Techniques': ['T1484'],

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,

            'OpsecSafe' : False,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': [
                'https://bit.ly/getbloodhound'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            # This one is only for empire
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            # These ones are for Invoke-BloodHound
            'CollectionMethod' : {
                'Description'   :   "The method to collect data. Group, LocalGroup, LocalAdmin, RDP, DCOM, PSRemote, Session, SessionLoop, Trusts, ACL, Container, ComputerOnly, GPOLocalGroup, LoggedOn, ObjectProps, SPNTargets, Default, DcOnly, All.",
                'Required'      :   True,
                'Value'         :   'Default'
            },
            'Stealth' : {
                'Description'   :   'Use stealth collection options, will sacrifice data quality in favor of much reduced network impact.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Domain' : {
                'Description'   :   'Specifies the domain to enumerate. If not specified, will enumerate the current domain your user context specifies.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'WindowsOnly' : {
                'Description'   :   'Limits computer collection to systems that have an operatingssytem attribute that matches *Windows*.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ComputerFile' : {
                'Description'   :   'A file, /!\ ON THE HOST /!\, containing a list of computers to enumerate. This option can only be used with the following Collection Methods: Session, SessionLoop, LocalGroup, ComputerOnly, LoggedOn.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LdapFilter' : {
                'Description'   :   'Append this ldap filter to the search filter to further filter the results enumerated.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'SearchBase' : {
                'Description'   :   'DistinguishedName to start LDAP searches at. Equivalent to the old --OU option.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'OutputDirectory' : {
                'Description'   :   'Folder to output files to.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'OutputDirectory' : {
                'Description'   :   'Folder to output files to.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'OutputPrefix' : {
                'Description'   :   'Prefix to add to output files.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'PrettyJSON' : {
                'Description'   :   'Output "pretty" json with formatting for readability.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'CacheFilename' : {
                'Description'   :   'Name for the cache file dropped to disk (default: unique hash generated per machine).',
                'Required'      :   False,
                'Value'         :   ''
            },
            'RandomFilenames' : {
                'Description'   :   'Randomize file names completely.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ZipFilename' : {
                'Description'   :   'Name for the zip file output by data collection.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'NoSaveCache' : {
                'Description'   :   'Don\'t write the cache file to disk. Caching will still be performed in memory.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'EncryptZip' : {
                'Description'   :   'Encrypt the zip file with a random password.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'NoZip' : {
                'Description'   :   'Do NOT zip the json files.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'InvalidateCache' : {
                'Description'   :   'Invalidate and rebuild the cache file.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LdapFilter' : {
                'Description'   :   'Append this ldap filter to the search filter to further filter the results enumerated.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'DomainController' : {
                'Description'   :   'Domain Controller to connect too. Specifiying this can result in data loss.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LdapPort' : {
                'Description'   :   'Port LDAP is running on. Defaults to 389/686 for LDAPS.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'SecureLDAP' : {
                'Description'   :   'Connect to LDAPS (LDAP SSL) instead of regular LDAP.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'DisableKerberosSigning' : {
                'Description'   :   'Disables keberos signing/sealing, making LDAP traffic viewable.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LdapUsername' : {
                'Description'   :   'Username for connecting to LDAP. Use this if you\'re using a non-domain account for connecting to computers.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LdapPassword' : {
                'Description'   :  'Password for connecting to LDAP. Use this if you\'re using a non-domain account for connecting to computers.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'SkipPortScan' : {
                'Description'   :  'Skip SMB port checks when connecting to computers.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'PortScanTimeout' : {
                'Description'   :   'Timeout for SMB port checks.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ExcludeDomainControllers' : {
                'Description'   :   'Exclude domain controllers from enumeration (usefult o avoid Microsoft ATP/ATA).',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Throttle' : {
                'Description'   :   'Throttle requests to computers (in milliseconds).',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Jitter' : {
                'Description'   :   'Add jitter to throttle.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'OverrideUserName' : {
                'Description'   :   'Override username to filter for NetSessionEnum.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'NoRegistryLoggedOn' : {
                'Description'   :   'Disable remote registry check in LoggedOn collection.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'DumpComputerStatus' : {
                'Description'   :   'Dumps error codes from attempts to connect to computers.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'RealDNSName' : {
                'Description'   :   'Overrides the DNS name used for API calls.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'CollectAllProperties' : {
                'Description'   :  'Collect all string LDAP properties on objects.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'StatusInterval' : {
                'Description'   :   'Interval for displaying status in milliseconds.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Loop' : {
                'Description'   :   'Perform looping for computer collection.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LoopDuration' : {
                'Description'   :   'Duration to perform looping (Default 02:00:00).',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LoopInterval' : {
                'Description'   :   'Interval to sleep between loops (Default 00:05:00).',
                'Required'      :   False,
                'Value'         :   ''
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
        
        moduleName = self.info["Name"]

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/situational_awareness/network/BloodHound3.ps1"
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

        script = "%s\n" %(moduleCode)
        scriptEnd = moduleName

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        scriptEnd += " -" + str(option)
                    else:
                        scriptEnd += " -" + str(option) + " " + str(values['Value']) 

        scriptEnd += ' | Out-String | %{$_ + \"`n\"};"`n'+str(moduleName)+' completed!"'
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        return script

