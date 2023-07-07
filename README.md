# cone-commands
collection of commonly used commands


## Remote Command 协议

### list命令
    
```shell
GET /list HTTP/1.1
Host:

HTTP/1.1 200 OK
Content-Type: application/json

{
    "commands": [
        {
            "name": "command1",
            "description": "command1 description"
        },
        {
            "name": "command2",
            "description": "command2 description"
        }
    ]
}

filter:
    name: string
    description: string
    
```

### execute命令

```shell
POST /execute HTTP/1.1
Host:

{
    "name": "command1",
    "args": [
        "arg1",
        "arg2"
    ]
}

HTTP/1.1 200 OK

{
    "result": "command1 result"
}

```

