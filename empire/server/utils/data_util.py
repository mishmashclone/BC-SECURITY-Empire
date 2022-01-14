import os
import subprocess

from empire.server.database import models
from empire.server.database.base import Session
from empire.server.common import helpers


def keyword_obfuscation(data):
    functions = Session().query(models.Function).all()

    for function in functions:
        data = data.replace(function.keyword, function.replacement)

    return data


def get_config(fields):
    """
    Helper to pull common database config information outside of the
    normal menu execution.

    Fields should be comma separated.
        i.e. 'version,install_path'
    """
    results = []
    config = Session().query(models.Config).first()

    for field in fields.split(','):
        results.append(config[field.strip()])

    return results


def get_listener_options(listener_name):
    """
    Returns the options for a specified listenername from the database outside
    of the normal menu execution.
    """
    try:
        listener_options = Session().query(models.Listener.options).filter(models.Listener.name == listener_name).first()
        return listener_options

    except Exception:
        return None


def obfuscate_module(moduleSource, obfuscationCommand="", forceReobfuscation=False):
    if is_obfuscated(moduleSource) and not forceReobfuscation:
        return

    try:
        with open(moduleSource, 'r') as f:
            moduleCode = f.read()
    except:
        print(helpers.color("[!] Could not read module source path at: " + moduleSource))
        return ""

    # Get the random function name generated at install and patch the stager with the proper function name
    moduleCode = keyword_obfuscation(moduleCode)

    # obfuscate and write to obfuscated source path
    path = os.path.abspath('server.py').split('server.py')[0] + "/"
    obfuscatedCode = obfuscate(os.getcwd() + '/empire/server', moduleCode, obfuscationCommand)
    obfuscatedSource = moduleSource.replace("module_source", "obfuscated_module_source")

    try:
        with open(obfuscatedSource, 'w') as f:
            f.write(obfuscatedCode)
    except:
        print(helpers.color("[!] Could not write obfuscated module source path at: " + obfuscatedSource))
        return ""


def obfuscate(installPath, psScript, obfuscationCommand):
    """
    Obfuscate PowerShell scripts using Invoke-Obfuscation
    """
    if not is_powershell_installed():
        print(helpers.color("[!] PowerShell is not installed and is required to use obfuscation, please install it first."))
        return ""
    # When obfuscating large scripts, command line length is too long. Need to save to temp file
    to_obfuscate_filename = installPath + "/data/misc/ToObfuscate.ps1"
    obfuscated_filename = installPath + "/data/misc/Obfuscated.ps1"

    # run keyword obfuscation before obfuscation
    ps_script = keyword_obfuscation(psScript)

    with open(to_obfuscate_filename, 'w') as toObfuscateFile:
        toObfuscateFile.write(ps_script)
    # Obfuscate using Invoke-Obfuscation w/ PowerShell
    subprocess.call(f"{get_powershell_name()} -C '$ErrorActionPreference = \"SilentlyContinue\";Import-Module {installPath}/powershell/Invoke-Obfuscation/Invoke-Obfuscation.psd1;Invoke-Obfuscation -ScriptPath {to_obfuscate_filename} -Command \"{convert_obfuscation_command(obfuscationCommand)}\" -Quiet | Out-File -Encoding ASCII {obfuscated_filename}'", shell=True)

    try:
        with open(obfuscated_filename, 'r') as obfuscatedFile:
            # Obfuscation writes a newline character to the end of the file, ignoring that character
            ps_script = obfuscatedFile.read()[0:-1]

        return ps_script
    except:
        print(helpers.color("[!] Could not write obfuscated module"))
        return ""

def is_obfuscated(moduleSource):
    obfuscatedSource = moduleSource.replace("module_source", "obfuscated_module_source")
    return os.path.isfile(obfuscatedSource)


def is_powershell_installed():
    return (get_powershell_name() != "")


def get_powershell_name():
    try:
        powershell_location = subprocess.check_output("which powershell", shell=True)
    except subprocess.CalledProcessError as e:
        try:
            powershell_location = subprocess.check_output("which pwsh", shell=True)
        except subprocess.CalledProcessError as e:
            return ""
        return "pwsh"
    return "powershell"


def convert_obfuscation_command(obfuscate_command):
    return "".join(obfuscate_command.split()).replace(",", ",home,").replace("\\", ",")
