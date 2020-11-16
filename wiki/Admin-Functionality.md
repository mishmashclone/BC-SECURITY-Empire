* [User Login](#User-Login)
* [User Logout](#User-Logout)
* [Restart the RESTful API Server](#restart-the-restful-api-server)
* [Shutdown the RESTful API Server](#shutdown-the-restful-api-server)

## User Login

### Handler

* **Handler** : POST /api/admin/login
* Description : Retrieves the API token given the correct username and password.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/admin/login -X POST -d '{"username":"empireadmin", "password":"Password123!"}'
```

**Response**:
```json
{
  "token": "ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5"
}
```
## User Logout

### Handler

* **Handler** : POST /api/admin/logout
* Description : Logs out of current user account.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/admin/logout -X POST
```

**Response**:
```json
{
  "success": "True"
}
```
## Restart the RESTful API Server

### Handler

* **Handler** : GET /api/restart
* Description : Restarts the RESTful API server.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/admin/restart?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "success": true
}
```

## Shutdown the RESTful API Server

### Handler

* **Handler** : GET /api/shutdown
* Description : Shutdown the RESTful API server.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/admin/shutdown?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "success": true
}
```