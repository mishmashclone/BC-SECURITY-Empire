Empire 4 Modules
================

Modules in Empire 4 are driven by a yaml configuration per module.
In most cases, only a yaml is needed to create a module. The fields are not much different from Empire <= 3. Just in a different place.

# Powershell

The [powershell_template.yaml](../empire/server/modules/powershell_template.yaml) will help guide through the fields needed for writing a simple module.
Of course, not every module will fit the simplest case. There are advanced options that we will discuss below.

The property `options` is a list of the options that can be set for the module at execution time.
All modules must contain an option called **Agent**. Additional options go in the options list after the **Agent** argument.
If the argument is required for execution, set `required: true`, and if a default value is warranted, set `value`.
The [prompt module](../empire/server/modules/powershell/collection/prompt.yaml) has an example of this.

When Empire boots up, it loads all module yamls found in the modules directory. If there are any missing fields or misconfigurations, the module won't load and a warning will print to the console.

##  Defining the script
**script:** For most scripts, simply pasting the script into the yaml is good enough.
```yaml
script: |
  Function Invoke-Template {
  
  }
```

**script_path:** For longer scripts, or scripts that are shared between multiple modules,
it is recommended to put the text file into the `empire/server/data/module_source` directory and reference it like so:
```yaml
script_path: 'empire/server/data/module_source/credentials/Invoke-Mimikatz.ps1'
```
The above example comes from the [logonpasswords module.](../empire/server/modules/powershell/credentials/mimikatz/logonpasswords.yaml)


**script_end:** In most cases the `script_end` will simply be a call to to the powershell function with a mustache template variable called `$PARAMS`.
`{{ PARAMS }}` is where Empire will insert the formatted options.
```yaml
script_end: Invoke-Function {{ PARAMS }}
```

There are functions that require the script_end to be customized a bit further. For example: the one found in [Invoke-Kerberoast](../empire/server/modules/powershell/credentials/invoke_kerberoast.yaml)
```yaml
script_end: Invoke-Kerberoast {{ PARAMS }} | fl | {{ OUTPUT_FUNCTION }} | %{$_ + "`n"};"`nInvoke-Kerberoast completed!
```

## Advanced
**custom_generate:** For complex modules that require custom code that accesses empire logic, such as lateral movement modules dynamically generating a listener launcher,
a custom "generate" function can be used in a similar way to Empire <= 3.
To tell Empire to utilize the custom generate function, set `advanced.custom_generate: true`
```yaml
advanced:
  custom_generate: true
```

The python file should share the same name as the yaml file. For example `Invoke-Assembly.yaml` and `Invoke-Assembly.py`
The generate function is a static function that gets passed 5 parameters:
- main_menu: The main_menu object that gives the module access to listeners, stagers, and just about everything else it might need
- module: The module, loaded from the yaml. In case we need to check properties like `opsec_safe`, `background`, etc.
- params: The execution parameters. At this point, Empire has already validated the parameters provided are the correct parameters for this module, and that the required parameters are there.
- obfuscate: Whether to obfuscate the code
- obfuscation_command: The command to use to obfuscate the code

It returns the generated code to be run by the agent as a string.

The generate function **should** treat these parameters as read only, to not cause side effects.
```python
class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = "") -> Tuple[Optiona[str], Optional[str]]:
        pass
```
Examples of modules that use this custom generate function:
- [bypassuac_eventvwr](../empire/server/modules/powershell/privesc/bypassuac_eventvwr.py)
- [invoke_assembly](../empire/server/modules/powershell/code_execution/invoke_assembly.py)
- [seatbelt](../empire/server/modules/powershell/situational_awareness/host/seatbelt.py)

If an error occurs during the execution of the generate function, return the error message using `handle_error_message`, which will ensure that
the client receives the error message in the REST response.

**option_format_string:** This tells Empire how to format all of the options before injecting them into the `script_end`.
In most cases, the default option format string will be fine: `-{{ KEY }} "{{ VALUE }}"`.

**option_format_string_boolean:** This tells Empire how to format boolean parameters when `True`.
In most cases, the default format string will be fine: `-{{ KEY }}`.

[Rubeus](../empire/server/modules/powershell/credentials/rubeus.yaml) is an example of a module that overwrites the option_format_string, since it only has one parameter `Command` and deviates from the default:
```yaml
options:
  - name: Agent
    description: Agent to run module on.
    required: true
    value: ''
  - name: Command
    description: Use available Rubeus commands as a one-liner.
    required: false
    value: ''
script_path: 'empire/server/data/module_source/credentials/Invoke-Rubeus.ps1'
script_end: "Invoke-Rubeus -Command \"{{ PARAMS }}\""
advanced:
  option_format_string: "{{ VALUE }}"
  option_format_string_boolean: ""
```

**name_in_code**: There may be times when you want the display name for an option in Starkiller/CLI to be different from how it looks in the module's code.
For this, you can use `name_in_code` such as in the [sharpsecdump module](../empire/server/modules/powershell/credentials/sharpsecdump.yaml)
```yaml
  - name: Username
    name_in_code: u
    description: Username to use, if you want to use alternate credentials to run. Must
      use with -p and -d flags, Misc)
    required: false
    value: ''
  - name: Password
    name_in_code: p
    description: Plaintext password to use, if you want to use alternate credentials
      to run. Must use with -u and -d flags
    required: false
    value: ''
```

**suggested_values**: A list of suggested values can be provided for an option.
These values will be available in the CLI and Starkiller as autocomplete values.
**strict**: If true, the option validator will check that the value chosen matches a value from
the suggested values list.

**OUTPUT_FUNCTION**: Some Powershell modules have an option named `OutputFunction` that converts the output to json, xml, etc.
The `OutputFunction` option can be inserted anywher in the `script` and `script_end` by using `{{ OUTPUT_FUNCTION }}`.
- An example of this in a yaml can be seen in [sherlock](../empire/server/modules/powershell/privesc/sherlock.yaml).
- If a module uses a `custom_generate` function, it needs to perform this substitution on its own.

# Python
Python modules are not much different from Powershell modules in terms of the yaml schema.
The differences for Python come in with the `script`, `script_path`, `script_end`, and option formatters.

A python script doesn't have an `option_format_string`. Instead, options are injected into the script directly using mustache templating.
An example of this is the python module [say](../empire/server/modules/python/trollsploit/osx/say.yaml)
```yaml
options:
  - name: Agent
    description: Agent to run module on.
    required: true
    value: ''
  - name: Text
    description:
    required: true
    value: 'The text to speak.'
  - name: Voice
    description: The voice to use.
    required: true
    value: 'alex'
script: run_command('say -v {{ Voice }} {{ Text }}')
```
Python modules also support the `advanced.custom_generate` method of generating the script.
Python modules can be used with `script` OR `script_path` and will ignore `script_end`, `option_format_string`, and `option_format_string_boolean`.

# C#
TODO
