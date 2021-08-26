# Hooks and Filters

## Empire 4.1 introduces a beta feature called hooks and filters.
*Since this is a beta feature, the api is subject to change at any point, until it is not beta.*

Hooks and filters are a function that a developer can implement that will be called when some event happens.

**Hooks** - Hooks are implemented to perform some side effect of an event happening. A hook does not need to return anything.

**Filters** - Filters are implemented to perform some modification of data after an event happens. A filter should return the modified arguments that it was given.

A minimal hook implementation.
```py
from empire.server.common.hooks import hooks

def my_hook(agent: models.Agent):
    """
    print to the console whenever an agent checks in.
    """
    print(f'New Agent Check in! Name: {agent.name}')
    
    
hooks.register_hook(hooks.AFTER_AGENT_CHECKIN_HOOK, 'checkin_logger_hook', my_hook)
```


A minimal filter implementation.
```py
from empire.server.common.hooks import hooks

def my_filter(tasking: models.Tasking):
    """
    Reverses the output string of a tasking.
    """
    tasking.output = tasking.output[::-1]
    
    return tasking

    
hooks.register_filter(hooks.BEFORE_TASKING_RESULT_FILTER, 'reverse_filter', my_filter)
```

Each event has its own set of unique arguments.
At the moment, the events are:
* AFTER_TASKING_HOOK

This event is triggered after the tasking is queued and written to the database.
Its arguments are (tasking: models.Tasking)

* BEFORE_TASKING_RESULT_HOOK/BEFORE_TASKING_RESULT_FILTER

This event is triggered after the tasking results are received but before they are written to the database.
Its arguments are (tasking: models.Tasking) where tasking is the db record.

* AFTER_TASKING_RESULT_HOOK

This event is triggered after the tasking results are received and after they are written to the database.
Its arguments are (tasking: models.Tasking) where tasking is the db record.

* AFTER_AGENT_CHECKIN_HOOK

This event is triggered after the agent has checked in and a record written to the database.
It has one argument (agent: models.Agent)

*The number of events at the moment is very minimal. If there's an event that you would like added, open an issue on the GitHub repo, come chat in our Discord, or put up a pull request.*

## Real World Examples
Empire utilizes both filters and hooks itself that can be used as a reference.

* The Powershell agent was updated to return JSON for some of the base shell commands. There are filters for `ls`, `ps`, `route`, and `ifconfig` that convert the JSON response to a table before it gets stored in the database.
* There is a hook implemented for the `ps` command that converts the results of `ps` from Powershell and Python agents into database records. The C# Agent is TODO.
* An example plugin that utilizes hooks is the [Twilio-Plugin](https://github.com/BC-SECURITY/Twilio-Plugin) which sends an operator a text message when an agent checks in.

Future enhancements:
* Since hooking the agent results events will invoke hooks on every single tasking result,
we'd like to implement something that is more module specific. For example, a module that needs to store credentials, such as Mimikatz, could have a `on_response` function in its `.py` file that is invoked specifically when that module returns.