from __future__ import print_function

from builtins import str
from builtins import object

from empire.server.utils import data_util
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        list_computers = params["IPs"]

        # read in the common powerview.ps1 module source code
        module_source = main_menu.installPath + "/data/module_source/situational_awareness/network/powerview.ps1"

        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        # get just the code needed for the specified function
        script = helpers.strip_powershell_comments(module_code)

        script += "\n" + """$Servers = Get-DomainComputer | ForEach-Object {try{Resolve-DNSName $_.dnshostname -Type A -errorAction SilentlyContinue}catch{Write-Warning 'Computer Offline or Not Responding'} } | Select-Object -ExpandProperty IPAddress -ErrorAction SilentlyContinue; $count = 0; $subarry =@(); foreach($i in $Servers){$IPByte = $i.Split("."); $subarry += $IPByte[0..2] -join"."} $final = $subarry | group; Write-Output{The following subnetworks were discovered:}; $final | ForEach-Object {Write-Output "$($_.Name).0/24 - $($_.Count) Hosts"}; """

        if list_computers.lower() == "true":
            script += "$Servers;"

        for option,values in params.items():
            if option.lower() != "agent":
                if values and values != '':
                    if values.lower() == "true":
                        # if we're just adding a switch
                        script += " -" + str(option)
                    else:
                        script += " -" + str(option) + " " + str(values)

        script += ' | Out-String | %{$_ + \"`n\"};"`n' + "get_subnet_ranges"+' completed!"'

        if obfuscate:
            script = helpers.obfuscate(main_menu.installPath, psScript=script, obfuscationCommand=obfuscation_command)
        script = data_util.keyword_obfuscation(script)

        return script

