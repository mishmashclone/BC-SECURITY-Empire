"""
Module handling functionality for Empire.
"""
from __future__ import absolute_import
from __future__ import print_function

import fnmatch
import importlib.util
import os
from builtins import object
from os import path
from typing import Dict, Optional, Tuple

import yaml

from empire.server.common import obfuscation
from empire.server.common.config import empire_config
from empire.server.common.module_models import PydanticModule, LanguageEnum
from empire.server.database import models
from empire.server.database.base import Session
from . import helpers


class Modules(object):

    def __init__(self, main_menu, args):

        self.main_menu = main_menu
        self.args = args

        self.modules: Dict[str, PydanticModule] = {}

        self._load_modules()

    def get_module(self, module_name: str) -> Optional[PydanticModule]:
        """
        Get a loaded module from in memory
        :param module_name: name
        :return: Optional[PydanticModule]
        """
        return self.modules.get(module_name)

    def execute_module(self, module: PydanticModule, params: Dict, user_id: int) \
            -> Tuple[Optional[Dict], Optional[str]]:
        """
        Execute the module.
        :param module: PydanticModule
        :param params: the execution parameters
        :param user_id: the user executing the module
        :return: tuple with the response and an error message (if applicable)
        """
        # TODO We need to start validating whether this module is valid for this agent language.
        cleaned_options, err = self._validate_module_params(module, params)

        if err:
            return None, err

        module_data = self._generate_script(module, cleaned_options, self.main_menu.obfuscate, self.main_menu.obfuscateCommand)
        if not module_data or module_data == "":
            return None, 'module produced an empty script'
        if not module_data.isascii():
            return None, 'module source contains non-ascii characters'

        if module.language == LanguageEnum.python:
            module_data = obfuscation.py_minify(module_data)
        elif module.language == LanguageEnum.powershell:
            module_data = helpers.strip_powershell_comments(module_data)

        session_id = params['Agent']
        task_command = ""
        # build the appropriate task command and module data blob
        if module.background:
            # if this module should be run in the background
            extension = module.output_extension
            if extension and extension != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                save_file_prefix = module.name.split("/")[-1]
                module_data = save_file_prefix.rjust(15) + extension.rjust(5) + module_data
                task_command = "TASK_CMD_JOB_SAVE"
            else:
                task_command = "TASK_CMD_JOB"

        else:
            # if this module is run in the foreground
            extension = module.output_extension
            if module.output_extension and module.output_extension != "":
                # if this module needs to save its file output to the server
                #   format- [15 chars of prefix][5 chars extension][data]
                save_file_prefix = module.name.split("/")[-1][:15]
                module_data = save_file_prefix.rjust(15) + extension.rjust(5) + module_data
                task_command = "TASK_CMD_WAIT_SAVE"
            else:
                task_command = "TASK_CMD_WAIT"

        # set the agent's tasking in the cache
        task_id = self.main_menu.agents.add_agent_task_db(session_id, task_command, module_data,
                                                          moduleName=module.name,
                                                          uid=user_id)

        # update the agent log
        msg = f"tasked agent {session_id} to run module {module.name}"
        self.main_menu.agents.save_agent_log(session_id, msg)

        if empire_config.yaml.get('modules.retain-last-value', True):
            self._set_default_values(module, cleaned_options)

        return {'success': True, 'taskID': task_id, 'msg': msg}, None

    def _validate_module_params(self, module: PydanticModule, params: Dict[str, str]) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        """
        Given a module and execution params, validate the input and return back a clean Dict for execution.
        :param module: PydanticModule
        :param params: the execution parameters
        :return: tuple with options and the error message (if applicable)
        """
        options = {}

        for option in module.options:
            if option.name in params:
                if option.name_in_code:
                    options[option.name_in_code] = params[option.name]
                else:
                    options[option.name] = params[option.name]
            elif option.required:
                return None, f'required module option missing: {option.name}'

        session_id = params['Agent']

        if not self.main_menu.agents.is_agent_present(session_id):
            return None, 'invalid agent name'

        module_version = float(module.min_language_version)
        agent_version = float(self.main_menu.agents.get_language_version_db(session_id))
        # check if the agent/module PowerShell versions are compatible
        if module_version > agent_version:
            return None, f"module requires PS version {module_version} but agent running PS version {agent_version}"

        if module.needs_admin:
            # if we're running this module for all agents, skip this validation
            if not self.main_menu.agents.is_agent_elevated(session_id):
                return None, 'module needs to run in an elevated context'

        return options, None

    @staticmethod
    def _set_default_values(module: PydanticModule, params: Dict):
        """
        Change the default values for the module loaded into memory.
        This is to retain the old empire behavior (and the behavior of stagers and listeners).
        :param module:
        :param params: cleaned param dictionary
        :return:
        """
        for option in module.options:
            if params.get(option.name):
                option.value = params[option.name]

    def _generate_script(self, module: PydanticModule, params: Dict, obfuscate=False, obfuscate_command='') -> str:
        """
        Generate the script to execute
        :param module: the execution parameters (already validated)
        :param params: the execution parameters
        :param obfuscate:
        :param obfuscate_command:
        :return: the generated script
        """
        if module.advanced.custom_generate:
            return module.advanced.generate_class.generate(self.main_menu, module, params, obfuscate, obfuscate_command)
        elif module.language == LanguageEnum.powershell:
            return self._generate_script_powershell(module, params, obfuscate, obfuscate_command)
        elif module.language == LanguageEnum.python:
            return self._generate_script_python(module, params)

    @staticmethod
    def _generate_script_python(module: PydanticModule, params: Dict):
        if module.script_path:
            with open(module.script_path, 'r') as stream:
                script = stream.read()
        else:
            script = module.script

        for key, value in params.items():
            if key.lower() != "agent" and key.lower() != "computername":
                script = script.replace('{{ ' + key + ' }}', value).replace('{{' + key + '}}', value)

        return script

    def _generate_script_powershell(self, module: PydanticModule, params: Dict, obfuscate=False, obfuscate_command=''):
        if module.script_path:
            # Get preobfuscated module code
            if obfuscate:
                helpers.obfuscate_module(moduleSource=module.script_path, obfuscationCommand=obfuscate_command)
                module_source = module.script_path.replace("module_source", "obfuscated_module_source")
                with open(module_source, 'r') as stream:
                    script = stream.read()
            else:
                with open(module.script_path, 'r') as stream:
                    script = stream.read()
        else:
            script = module.script

        script_end = f" {module.script_end} "
        option_strings = []
        for key, value in params.items():
            if key.lower() != "agent" and key.lower() != "computername":
                if value and value != '':
                    if value.lower() == "true":
                        # if we're just adding a switch
                        # wannabe mustache templating.
                        # If we want to get more advanced, we can import a library for it.
                        this_option = module.advanced.option_format_string_boolean \
                            .replace('{{ KEY }}', str(key)) \
                            .replace('{{KEY}}', str(key))
                        option_strings.append(f'{this_option}')
                    else:
                        this_option = module.advanced.option_format_string \
                            .replace('{{ KEY }}', str(key)) \
                            .replace('{{KEY}}', str(key)) \
                            .replace('{{ VALUE }}', str(value)) \
                            .replace('{{VALUE}}', str(value))
                        option_strings.append(f'{this_option}')

        script_end = script_end \
            .replace('{{ PARAMS }}', ' '.join(option_strings)) \
            .replace('{{PARAMS}}', ' '.join(option_strings))

        script += script_end

        if obfuscate:
            script = helpers.obfuscate(self.main_menu.installPath, psScript=script, obfuscationCommand=obfuscate_command)
        script = helpers.keyword_obfuscation(script)

        return script

    def _load_modules(self, root_path=''):
        """
        Load Empire modules from a specified path, default to
        installPath + "/modules/*"
        """
        if root_path == '':
            root_path = f"{self.main_menu.installPath}/modules/"

        print(helpers.color(f"[*] Loading modules from: {root_path}"))
         
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                if not filename.lower().endswith('.yaml') and not filename.lower().endswith('.yml'):
                    continue

                file_path = os.path.join(root, filename)

                # don't load up any of the templates
                if fnmatch.fnmatch(filename, '*template.yaml'):
                    continue

                # instantiate the module and save it to the internal cache
                try:
                    self._load_module(root_path, file_path)
                except Exception as e:
                    print(e)

        Session().commit()

    def _load_module(self, root_path, file_path: str):
        # extract just the module name from the full path
        module_name = file_path.split(root_path)[-1][0:-5]

        if root_path != f"{self.main_menu.installPath}/modules/":
            module_name = f"external/{module_name}"

        with open(file_path, 'r') as stream:
            yaml2 = yaml.safe_load(stream)
            # remove None values so pydantic can apply defaults
            yaml3 = {k: v for k, v in yaml2.items() if v is not None}
            my_model = PydanticModule(**yaml3)

            if my_model.advanced.custom_generate:
                if not path.exists(file_path[:-4] + "py"):
                    raise Exception("No File to use for custom generate.")
                spec = importlib.util.spec_from_file_location(module_name + ".py", file_path[:-5] + ".py")
                imp_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(imp_mod)
                my_model.advanced.generate_class = imp_mod.Module()
            elif my_model.script_path:
                if not path.exists(my_model.script_path):
                    raise Exception("File provided in script_path does not exist.")
            elif my_model.script:
                pass
            else:
                raise Exception("Must provide a valid script, script_path, or custom generate function")

            mod = Session().query(models.Module).filter(models.Module.name == module_name).first()

            if not mod:
                mod = models.Module(name=module_name, enabled=True)
                Session().add(mod)

            self.modules[module_name] = my_model
            self.modules[module_name].enabled = mod.enabled
