import threading
import time

from empire.client.src.EmpireCliState import state
from empire.client.src.menus.Menu import Menu
from empire.client.src.utils import print_util
from empire.client.src.utils.autocomplete_util import position_util
from empire.client.src.utils.cli_util import register_cli_commands


@register_cli_commands
class ShellMenu(Menu):
    def __init__(self):
        super().__init__(display_name='', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            print('Exit Shell Menu with ctrl-c')
            return True

    def get_prompt(self) -> str:
        return f"<ansiblue>({self.selected})</ansiblue> <ansired>{self.display_name}</ansired> > "

    def tasking_id_returns(self, agent_name, task_id: int):
        """
        Polls and prints tasking data for taskID

        Usage: tasking_id_returns <agent_name> <task_id>
        """
        # todo: there must be a better way to do this with notifications
        # todo: add a timeout value
        # Set previous results to current results to avoid a lot of old data
        status_result = False

        while not status_result:
            try:
                results = state.get_agent_result(agent_name)['results'][0]['AgentResults'][task_id - 1]
                if results['results'] is not None:
                    print(print_util.color(results['results']))
                    status_result = True
            except:
                pass
            time.sleep(1)

    def use(self, agent_name: str) -> None:
        """
        Use shell

        Usage: shell
        """
        self.selected = agent_name
        self.session_id = state.agents[self.selected]['session_id']
        self.language = state.agents[self.selected]['language']
        if self.language == 'powershell':
            self.powershell_update_directory(self.session_id)
        elif self.language == 'python':
            self.python_update_directory(self.session_id)

    def powershell_update_directory(self, session_id: str):
        """
        Update current directory

        Usage:  update_directory <session_id>
        """
        temp_name = None
        task_id: str = str(state.agent_shell(session_id, '(Resolve-Path .\).Path')['taskID'])

        # Retrieve directory results and wait for response
        while temp_name is None:
            try:
                temp_name = state.get_task_result(session_id, task_id)['results']
            except:
                pass
            time.sleep(1)
        self.display_name = temp_name
        self.get_prompt()

    def python_update_directory(self, session_id: str):
        """
        Update current directory

        Usage:  update_directory <session_id>
        """
        temp_name = None
        task_id: str = str(state.agent_shell(session_id, 'echo $PWD')['taskID'])

        # Retrieve directory results and wait for response
        while temp_name is None:
            try:
                temp_name = state.get_task_result(session_id, task_id)['results'].split('\r')[0]
            except:
                pass
            time.sleep(1)
        self.display_name = temp_name
        self.get_prompt()

    def shell(self, agent_name: str, shell_cmd: str):
        """
        Tasks an the specified agent_name to execute a shell command.

        Usage:  <shell_cmd>
        """
        response = state.agent_shell(agent_name, shell_cmd)
        if shell_cmd.split()[0].lower() in ['cd', 'set-location']:
            if self.language == 'powershell':
                shell_return = threading.Thread(target=self.powershell_update_directory, args=[agent_name])
                shell_return.daemon = True
                shell_return.start()
            elif self.language == 'python':
                shell_return = threading.Thread(target=self.python_update_directory, args=[agent_name])
                shell_return.daemon = True
                shell_return.start()
        else:
            shell_return = threading.Thread(target=self.tasking_id_returns, args=[self.session_id, response['taskID']])
            shell_return.daemon = True
            shell_return.start()


shell_menu = ShellMenu()
