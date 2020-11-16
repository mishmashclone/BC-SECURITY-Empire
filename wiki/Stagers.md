* [Get Current Stagers](#get-current-stagers)
* [Get Stager by Name](#get-stager-by-name)
* [Generate Stager](#generate-stager)

## Get Current Stagers

### Handler

* **Handler** : GET /api/stagers
* Description : Returns all current Empire stagers and options.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/stagers?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "stagers": [
    {
      "Author": [
        "@harmj0y"
      ],
      "Comments": [
        ""
      ],
      "Description": "Generates a ducky script that runes a one-liner stage0 launcher for Empire.",
      "Name": "ducky",
      "options": {
        "Listener": {
          "Description": "Listener to generate stager for.",
          "Required": true,
          "Value": ""
        },
        "OutFile": {
          "Description": "File to output duckyscript to.",
          "Required": true,
          "Value": ""
        },
        "Proxy": {
          "Description": "Proxy to use for request (default, none, or other).",
          "Required": false,
          "Value": "default"
        },
        "ProxyCreds": {
          "Description": "Proxy credentials ([domain\\]username:password) to use for request (default, none, or other).",
          "Required": false,
          "Value": "default"
        },
        "StagerRetries": {
          "Description": "Times for the stager to retry connecting.",
          "Required": false,
          "Value": "0"
        },
        "UserAgent": {
          "Description": "User-agent string to use for the staging request (default, none, or other).",
          "Required": false,
          "Value": "default"
        }
      }
    },
    ...
  ]
}
```

## Get Stager by Name

### Handler

* **Handler** : GET /api/stagers/STAGER_NAME
* Description : Returns the Empire stager specified by STAGER_NAME.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/stagers/dll?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "stagers": [
    {
      "Author": [
        "@sixdub"
      ],
      "Comments": [
        ""
      ],
      "Description": "Generate a PowerPick Reflective DLL to inject with stager code.",
      "Name": "dll",
      "options": {
        "Arch": {
          "Description": "Architecture of the .dll to generate (x64 or x86).",
          "Required": true,
          "Value": "x64"
        },
        "Listener": {
          "Description": "Listener to use.",
          "Required": true,
          "Value": ""
        },
        "OutFile": {
          "Description": "File to output dll to.",
          "Required": true,
          "Value": "/tmp/launcher.dll"
        },
        "Proxy": {
          "Description": "Proxy to use for request (default, none, or other).",
          "Required": false,
          "Value": "default"
        },
        "ProxyCreds": {
          "Description": "Proxy credentials ([domain\\]username:password) to use for request (default, none, or other).",
          "Required": false,
          "Value": "default"
        },
        "StagerRetries": {
          "Description": "Times for the stager to retry connecting.",
          "Required": false,
          "Value": "0"
        },
        "UserAgent": {
          "Description": "User-agent string to use for the staging request (default, none, or other).",
          "Required": false,
          "Value": "default"
        }
      }
    }
  ]
}
```

## Generate Stager

### Handler

* **Handler** : POST /api/stagers
* Description : Returns the Empire stager specified by parameters.
* Parameters :
  * StagerName  : the stager name to generate (required)
  * Listener    : the listener name to generate the stager for (required)
  * *additional*    : any additional stager values enumerated from stager options

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/stagers?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -X POST -d '{"StagerName":"launcher", "Listener":"testing"}'
```

**Response**:
```json
{
  "launcher": {
    "Base64": {
      "Description": "Switch. Base64 encode the output.",
      "Required": true,
      "Value": "True"
    },
    "Listener": {
      "Description": "Listener to generate stager for.",
      "Required": true,
      "Value": "testing"
    },
    "OutFile": {
      "Description": "File to output launcher to, otherwise displayed on the screen.",
      "Required": false,
      "Value": ""
    },
    "Output": "powershell.exe -NoP -sta -NonI -W Hidden -Enc JAB...KQA=",
    "Proxy": {
      "Description": "Proxy to use for request (default, none, or other).",
      "Required": false,
      "Value": "default"
    },
    "ProxyCreds": {
      "Description": "Proxy credentials ([domain\\]username:password) to use for request (default, none, or other).",
      "Required": false,
      "Value": "default"
    },
    "StagerRetries": {
      "Description": "Times for the stager to retry connecting.",
      "Required": false,
      "Value": "0"
    },
    "UserAgent": {
      "Description": "User-agent string to use for the staging request (default, none, or other).",
      "Required": false,
      "Value": "default"
    }
  }
}
```
