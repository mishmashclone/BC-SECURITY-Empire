import threading
import time

from prompt_toolkit.completion import Completion

from empire.client.src.EmpireCliState import state
from empire.client.src.menus.UseMenu import UseMenu
from empire.client.src.utils import print_util
from empire.client.src.utils.autocomplete_util import filtered_search_list, position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class UseModuleMenu(UseMenu):
    def __init__(self):
        super().__init__(display_name='usemodule', selected='', record=None, record_options=None)

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] == 'usemodule' and position_util(cmd_line, 2, word_before_cursor):
            for module in filtered_search_list(word_before_cursor, state.modules.keys()):
                yield Completion(module, start_position=-len(word_before_cursor))
        else:
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def tasking_id_returns(self, agent_name, task_id: int):
        """
        Polls and prints tasking data for taskID

        Usage: tasking_id_returns <agent_name> <task_id>
        """
        # todo: there must be a better way to do this with notifications
        # Set previous results to current results to avoid a lot of old data
        status_result = False

        while not status_result:
            try:
                results = state.get_agent_result(agent_name)['results'][0]['AgentResults'][task_id - 1]
                if results['results'] is not None:
                    if 'Job started:' not in results['results']:
                        print(print_util.color('[*] Task ' + str(results['taskID']) + " results received"))
                        print(print_util.color(results['results']))
                        status_result = True
            except:
                pass
            time.sleep(1)

    def on_enter(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])

            if 'agent' in kwargs and 'Agent' in self.record_options:
                self.set('Agent', kwargs['agent'])
            self.info()
            self.options()
            return True

    def use(self, module: str) -> None:
        """
        Use the selected module

        Usage: use <module>
        """
        if module in state.modules.keys():
            self.selected = module
            self.record = state.modules[module]
            self.record_options = state.modules[module]['options']

    @command
    def execute(self):
        """
        Execute the selected module

        Usage: execute
        """
        # todo validation and error handling
        # Hopefully this will force us to provide more info in api errors ;)
        post_body = {}
        for key, value in self.record_options.items():
            post_body[key] = self.record_options[key]['Value']

        response = state.execute_module(self.selected, post_body)
        if 'success' in response.keys():
            print(print_util.color(
                '[*] Tasked ' + self.record_options['Agent']['Value'] + ' to run Task ' + str(response['taskID'])))
            agent_return = threading.Thread(target=self.tasking_id_returns,
                                            args=[self.record_options['Agent']['Value'], response['taskID']])
            agent_return.daemon = True
            agent_return.start()
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def generate(self):
        """
        Execute the selected module

        Usage: generate
        """
        self.execute()


use_module_menu = UseModuleMenu()
