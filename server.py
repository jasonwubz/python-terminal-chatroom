#!/usr/bin/env python3
# Copyright 2019 Jiacheng Wu <jia.cheng.wu@gmail.com>

import socket
import sys
import threading
import datetime

SERVER_PORT = 50009

def PrintMessage(message):
    print("{} {}".format(datetime.datetime.now().time(), message))

try:
    # create socket, SOCK_STREAM means it will use TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind with empty address to allow any connection from the network
    server_socket.bind(('', SERVER_PORT))

    server_socket.listen(socket.SOMAXCONN)

except socket.error as err: 
    PrintMessage("fatal:socket creation failed with error {}".format(err))
    # exit with error code
    sys.exit(1)

def Broadcast(message, who="SERVER", skip=None, is_action=False):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    for index in list(client_sockets):
        if client_sockets[index] is skip: 
            continue
        else:
            if is_action:
                client_sockets[index].send("{} \33[41m{}\33[0m \r\n".format(ts, message.strip()).encode())
            else:
                client_sockets[index].send("{} \33[41m{}\33[0m said: {}\r\n".format(ts, who, message.strip()).encode())

def GetClientID(client):
    for index in list(client_sockets):
        if client_sockets[index] is client:
            return index

def RemoveClient(client):
    for index in list(client_sockets):
        if client_sockets[index] is client: 
            PrintMessage(f"removing client from list {index}")
            del client_sockets[index]

def HandleClient(client, client_id): 
    
    # send welcome 
    client.send("""
\r\n
\33[42;30m OH NO! NOT ANOTHER TERMINAL CHAT ROOM! \33[0m\r\n
Welcome! There are \33[44m {} \33[0m client(s) connected.\r\n
Say something! Type 'exit' to end chat, 'shutdown' to end server.     
""".format(len(client_sockets)-1).encode())

    client.send("\n\r".encode())

    Broadcast("new client joined the chat", "SERVER", client)

    string_to_send = ''
    buffer = []

    # data received from client 
    while True:
        try:
            data = client.recv(1) 
        except socket.error as err:
            PrintMessage(f"error:socket error occurred on client thread {err}")
            client.close()
            break
        except:
            PrintMessage("error:unhandled error in client")
            break

        if not data: 
            PrintMessage('error:unable to recieve from client')
            break 
        else:
            buffer.append(data)

            string_to_send = ''.join(x.decode('utf-8') for x in buffer)
            if string_to_send.find("\n") != -1:
                # removes newline and carriage return from received bytes
                str_to_print = string_to_send.strip()

                # clears buffer
                buffer = []
            
                PrintMessage(f"\33[41m{client_id}\33[0m said({len(string_to_send)}): {str_to_print}") 

                # sends broadcast to others
                
                if str_to_print == "exit":
                    PrintMessage("notice:client issues exit command")

                    # sends client good bye and notify other connections
                    Broadcast("client {} has left the chat".format(client_id), "", client, True)

                    RemoveClient(client)
                    break
                elif str_to_print == "shutdown":
                    # uh oh!
                    PrintMessage("warning:client issues shutdown")
                    Broadcast("server is shutting down :(", "SERVER")
                    try:
                        server_socket.shutdown(socket.SHUT_RDWR)                        
                    except:
                        server_socket.close()
                        # PrintMessage(f"unexpected error in shutdown command {sys.exc_info()}")
                    break
                else:
                    Broadcast(str_to_print, client_id, client)

            # send back reversed string to client 
            # client.send("you said something".encode())
    
    # connection closed 
    PrintMessage("notice:thread exiting")
    client.close()    

client_threads = list()

# a disctionary of clients socket since a set can only contain unique values
client_sockets = {}

PrintMessage(f"server started on port {SERVER_PORT}")

while True:
    try:
        # accept new connection
        new_client, client_address = server_socket.accept()
        PrintMessage(f"client connected from {client_address}")
        
        #create client id out of their address and port
        cli_ip, cli_port = client_address
        cli_id = cli_ip + ':' + str(cli_port)

        PrintMessage(f"client ID is \33[43;30m{cli_id}\33[0m")

        # launch thread        
        cli_thread = threading.Thread(target=HandleClient, args=(new_client,cli_id,))

        client_sockets[cli_id] = new_client
        cli_thread.start()
        client_threads.append(cli_thread)
    except (OSError, WindowsError):
        PrintMessage("notice:server closing")
        if server_socket:
            server_socket.close()
        for index in client_sockets:
            if client_sockets[index]: 
                PrintMessage(f"closing client {index}")
                client_sockets[index].close()
        break
    except:
        print(f"unexpected error caught {sys.exc_info()}")
        break

# join all threads
for index, thread in enumerate(client_threads):
    thread.join()
    PrintMessage(f"closing thread {index} done")