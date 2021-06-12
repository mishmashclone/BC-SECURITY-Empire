## Configuration
The Empire Client and Empire Server both have a config.yaml file to customize behavior.

### Server
The Server configuration is managed via [empire/server/config.yaml](../empire/server/config.yaml).
- **suppress-self-cert-warning** - Suppress the http warnings when launching an Empire instance that uses a self-signed cert

- **database** - Configure Empire's database. Empire defaults to SQLite and has the ability to run with MySQL.

SQLite - The location of the SQLite db file is configurable.
```yaml
database:
  type: sqlite
  location: empire/server/data/empire.db
```

MySQL (Beta) - The url, username, and password are all configurable.
Everything in Empire should be working with MySQL with the exception of Python agents.
There is additional work needed in order to support them.
```yaml
database:
  type: mysql
  url: localhost
  username:
  password:
```

The defaults block defines the properties that are initially loaded into the database when it is first created.
```yaml
database:
  defaults:
    # staging key will first look at OS environment variables, then here.
    # If empty, will be prompted (like Empire <3.7).
    staging-key: RANDOM
    username: empireadmin
    password: password123
    obfuscate: false
    # Note the escaped backslashes
    obfuscate-command: "Token\\All\\1"
    # an IP white list to ONLY accept clients from
    #   format is "192.168.1.1,192.168.1.10-192.168.1.100,10.0.0.0/8"
    ip-whitelist: ""
    # an IP black list to reject accept clients from
    #   format is "192.168.1.1,192.168.1.10-192.168.1.100,10.0.0.0/8"
    ip-blacklist: ""
```

- **modules.retain-last-value** - This tells Empire to retain the last values set for a module.
In Empire 4.0, the modules objects were converted to be stateless, so when a user executes a module,
it doesn't impact the values seen or set by another user. Set this to `true` if you want to mimic the old
behavior.

### Client
The Client configuration is managed via [empire/client/config.yaml](../empire/client/config.yaml).

- **servers** - The servers block is meant to give the user the ability to set up frequently used Empire servers.
If a server is listed in this block then when connecting to the server they need only type: `connect -c localhost`.
This tells the client to use the connection info for the server named localhost from the yaml. In addition, if autoconnect is set to `true`, the client will automatically connect to that server when starting up.
```yaml
servers:
  localhost:
    host: https://localhost
    port: 1337
    socketport: 5000
    username: empireadmin
    password: password123
    autoconnect: true
```
- **suppress-self-cert-warning** - Suppress the http warnings when connecting to an Empire instance that uses a self-signed cert
- **shortcuts** - Shortcuts defined here allow the user to define their own frequently used modules and assign a command to them.
Let's look at 3 distinct examples. All of which can be found in the default [config.yaml](../empire/client/config.yaml)
```yaml
shortcuts:
  powershell:
    sherlock:
      module: powershell/privesc/sherlock
```
This first example is the simplest example. It adds a `sherlock` command to the Interact menu for Powershell agents. It does not pass any specific parameters.

```yaml
shortcuts:
  powershell:
    keylog:
      module: powershell/collection/keylogger
      params:
        - name: Sleep
          value: 1
```
This next one is slightly more complex in that we are telling the shortcut to set the *Sleep* parameter to 1.
Note that if there are any other parameters for this module that we don't define, it will use whatever the default value is.

```yaml
shortcuts:
  powershell:
    bypassuac:
      module: powershell/privesc/bypassuac_eventvwr
      params:
        - name: Listener
          dynamic: true
```
This third one gets a bit more complex. Instead of providing a `value` to the parameter, it is marked as `dynamic`.
This tells the CLI that it expects the user to send the parameters as part of their command. In other words the user needs to type `bypassuac http1` in order for this to execute.
The parameters are passed in the order they are defined in config.yaml. There are some convenient autocompletes if the field is named `Listener` or `Agent`.

```yaml
shortcuts:
  powershell:
    whoami:
      shell: whoami
```
The last one is much more simple. Instead of running a module, we run a shell command.

- **resource-file** - A resource file is simply a text file with a list of commands to run in order.
An example txt is shown below
```yaml
resource-file: commands.txt

# commands.txt
listeners
uselistener http
set Port 999
execute
```
