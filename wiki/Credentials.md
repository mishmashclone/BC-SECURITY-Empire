## Get Stored Credentials

### Handler

* **Handler** : GET /api/creds
* Description : Returns all credentials currently stored in an Empire server.
* No parameters

### Example

**Request**:
```bash
curl --insecure -i https://localhost:1337/api/creds?token=ks23jlvdki4fj1j23w39h0h0xcuwjrqilocxd6b5
```

**Response**:
```json
{
  "creds": [
    {
      "ID": 1,
      "credtype": "hash",
      "domain": "testlab.local",
      "host": "WINDOWS1",
      "notes": "2016-03-31 17:37:23",
      "password": "2b576acbe6b...",
      "sid": "S-1-5-21-664317401-282805101-...",
      "username": "Administrator"
    },
    ...
  ]
}
```