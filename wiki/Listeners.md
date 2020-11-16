* [Get Current Listeners](#get-current-listeners)
* [Get Listener by Name](#get-listener-by-name)
* [Get Current Listener Options](#get-current-listener-options)
* [Create a Listener](#create-a-listener)
* [Kill a Listener](#kill-a-listener)
* [Kill All Listeners](#kill-all-listeners)

## Get Current Listeners

### Handler

* **Handler** : GET /api/listeners
* Description : Returns all current Empire listeners.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/listeners?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "listeners": [
    {
      "ID": 1,
      "cert_path": "",
      "default_delay": 5,
      "default_jitter": 0.0,
      "default_lost_limit": 60,
      "default_profile": "/admin/get.php,/news.asp,/login/process.jsp|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
      "host": "http://192.168.52.172:8080",
      "kill_date": "",
      "listener_type": "native",
      "name": "test",
      "port": 8080,
      "redirect_target": "",
      "staging_key": "m@T%L?V...",
      "working_hours": ""
    }
  ]
}
```

## Get Listener by Name

### Handler

* **Handler** : GET /api/listeners/LISTENER_NAME
* Description : Returns the listener specifed by the name/id LISTENER_NAME.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/listeners/test?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "listeners": [
    {
      "ID": 1,
      "cert_path": "",
      "default_delay": 5,
      "default_jitter": 0.0,
      "default_lost_limit": 60,
      "default_profile": "/admin/get.php,/news.asp,/login/process.jsp|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
      "host": "http://192.168.52.172:8080",
      "kill_date": "",
      "listener_type": "native",
      "name": "test",
      "port": 8080,
      "redirect_target": "",
      "staging_key": "m@T%L...",
      "working_hours": ""
    }
  ]
}
```

## Get Current Listener Options

### Handler

* **Handler** : GET /api/listeners/options/listener_type
* Description : Returns the current listener options for the specified type.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/listeners/options/http?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "listeneroptions": [
    {
      "CertPath": {
        "Description": "Certificate path for https listeners.",
        "Required": false,
        "Value": ""
      },
      "DefaultDelay": {
        "Description": "Agent delay/reach back interval (in seconds).",
        "Required": true,
        "Value": 5
      },
      "DefaultJitter": {
        "Description": "Jitter in agent reachback interval (0.0-1.0).",
        "Required": true,
        "Value": 0.0
      },
      "DefaultLostLimit": {
        "Description": "Number of missed checkins before exiting",
        "Required": true,
        "Value": 60
      },
      "DefaultProfile": {
        "Description": "Default communication profile for the agent.",
        "Required": true,
        "Value": "/admin/get.php,/news.asp,/login/process.jsp|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
      },
      "Host": {
        "Description": "Hostname/IP for staging.",
        "Required": true,
        "Value": "http://192.168.52.173:8080"
      },
      "KillDate": {
        "Description": "Date for the listener to exit (MM/dd/yyyy).",
        "Required": false,
        "Value": ""
      },
      "Name": {
        "Description": "Listener name.",
        "Required": true,
        "Value": "test"
      },
      "Port": {
        "Description": "Port for the listener.",
        "Required": true,
        "Value": "8080"
      },
      "RedirectTarget": {
        "Description": "Listener target to redirect to for pivot/hop.",
        "Required": false,
        "Value": ""
      },
      "StagingKey": {
        "Description": "Staging key for initial agent negotiation.",
        "Required": true,
        "Value": "m@T%L..."
      },
      "Type": {
        "Description": "Listener type (native, pivot, hop, foreign, meter).",
        "Required": true,
        "Value": "native"
      },
      "WorkingHours": {
        "Description": "Hours for the agent to operate (09:00-17:00).",
        "Required": false,
        "Value": ""
      }
    }
  ]
}
```

## Create a Listener

### Handler

* **Handler** : POST /api/listeners/listener_type
* Description : Creates a listener with the specified parameters.
* Parameters (none required) :
  * Name    : name for the listener
  * *additional*    : any additional values enumerated from listener options above

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/listeners/http?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -X POST -d '{"Name":"testing"}'
```

**Response**:
```json
{
  "msg": "listener 'testing' successfully started.",
  "success": true
}
```

### Failure Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/listeners/http?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -X POST -d '{"Name":"testing"}'
```

**Response**:
```json
{
  "msg": "Error starting listener on port 8080, port likely already in use.",
  "success": false
}
```

## Kill a Listener

### Handler

* **Handler** : DELETE /api/listeners/LISTENER_NAME
* Description : Kills the listener specifed by the name/id LISTENER_NAME.
* No parameters

#### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/listeners/testing?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -X DELETE
```

**Response**:
```json
{
  "success": true
}
```

## Kill All Listeners

### Handler

* **Handler** : DELETE /api/listeners/all
* Description : Kills all listeners.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/listeners/all?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5 -X DELETE
```

**Response**:
```json
{
  "success": true
}
```