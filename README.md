# Python Terminal Chatroom

Oh No! Not another terminal chatroom! Oh yes boys and girls! This time in python!

This is an experimental project done while I was learning python essentials. The project can be used as a standalone terminal chat room. The idea of this project is borrowed from my PHP terminal chatroom project as a way for me to learn how TCP socket connections can be handled using threading. The major advantage of threading is that it handle concurrency.

This is only a purely experimental project and care should be taken when using this in a network as I have not done any special character escaping. Have fun!

## Prerequisites

You will need at least Python 3.7

## Getting Started

You may configure the port that you want to bind the chat server to in the configuration file (config.ini):

```ini
[SOCKET]
server_port = 50009
```

Next, in your terminal, simply type the following command to start the chat server.


```sh
$ py server.py
```

Clients can use telnet to connect to the chat room:


```sh
$ telnet 127.0.0.1 50009
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


