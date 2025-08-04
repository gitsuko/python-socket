# python-socket app
A command-line socket program written in Python.

## Features

- One server handling multiple clients
- No blocking for sending or receiving messages
- Retrieves host IP address with `get_ip.py` script
- Uses Python's built-in `socket` and `threading` modules
- Uses a Python dictionary to manage active client connections (socket, IP, port)

## Usage

### Run server script.

```bash
python3 server.py
```

### Run client script (you can open multiple)

```bash
python3 client.py
```