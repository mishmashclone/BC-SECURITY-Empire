import string

from prompt_toolkit.completion import Completion

from empire.client.src.EmpireCliState import state
from empire.client.src.menus.Menu import Menu
from empire.client.src.utils import table_util, print_util, date_util
from empire.client.src.utils.autocomplete_util import filtered_search_list, position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class AgentMenu(Menu):
    def __init__(self):
        super().__init__(display_name='agents', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['kill', 'clear', 'rename'] and position_util(cmd_line, 2, word_before_cursor):
            for agent in filtered_search_list(word_before_cursor, state.agents.keys()):
                yield Completion(agent, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self):
        self.list()
        return True

    @command
    def list(self) -> None:
        """
        Get running/available agents

        Usage: list
        """
        agent_list = []
        agent_formatting = []
        for agent in state.get_agents().values():
            agent_list.append([str(agent['ID']), agent['name'],
                               agent['language'], agent['internal_ip'], print_util.text_wrap(agent['username']),
                               print_util.text_wrap(agent['process_name'],width=20), agent['process_id'],
                               str(agent['delay']) + '/' + str(agent['jitter']),
                               date_util.humanize_datetime(agent['lastseen_time']), agent['listener']])
            agent_formatting.append([agent['stale'], agent['high_integrity']])

        agent_formatting.insert(0, ['Stale', 'High Integrity'])
        agent_list.insert(0, ['ID', 'Name', 'Language', 'Internal IP', 'Username', 'Process',
                              'PID', 'Delay', 'Last Seen', 'Listener'])
        table_util.print_agent_table(agent_list, agent_formatting, 'Agents')

    @command
    def kill(self, agent_name: string) -> None:
        """
        Kill the selected listener

        Usage: kill <agent_name>
        """
        state.kill_agent(agent_name)

    @command
    def clear(self, agent_name: string) -> None:
        """
        Clear tasks for selected listener

        Usage: clear <agent_name>
        """
        state.clear_agent(agent_name)

    @command
    def remove(self, agent_name: string) -> None:
        """
        Removes an agent from the controller specified by agent_name. Doesn't kill the agent first.

        Usage: remove <agent_name>
        """
        response = state.remove_agent(agent_name)
        if 'success' in response.keys():
            print(print_util.color('[*] Removed agent ' + agent_name))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def rename(self, agent_name: string, new_agent_name: string) -> None:
        """
        Rename selected listener

        Usage: rename <agent_name> <new_agent_name>
        """
        state.rename_agent(agent_name, new_agent_name)


def trunc(value: string = '', limit: int = 1) -> string:
    if value:
        if len(value) > limit:
            return value[:limit - 2] + '..'
        else:
            return value
    return ''


agent_menu = AgentMenu()
