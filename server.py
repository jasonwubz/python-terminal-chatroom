#!/usr/bin/env python3
# Copyright 2019 Jiacheng Wu

import socket
import sys
import threading

SERVER_PORT = 50009

try:
    # create socket, SOCK_STREAM means it will use TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind with empty address to allow any connection from the network
    server_socket.bind(('', SERVER_PORT))

    server_socket.listen(socket.SOMAXCONN)

except socket.error as err: 
    print("socket creation failed with error {}".format(err))
    # exit with error code
    sys.exit(1)

def RemoveClient(client):
    for index, tclient in enumerate(client_sockets):
        if tclient is client: 
            print(f"removing client from list {index}")
            client_sockets.remove(tclient)

def HandleClient(client): 
    
    # send welcome 
    client.send("welcome to this chatroom\n\r".encode())

    string_to_send = ''
    buffer = []

    # data received from client 
    while True:
        try:
            data = client.recv(1) 
        except socket.error as err:
            print(f"socket error occurred on client thread {err}")
            client.close()
            break
        except:
            print("unhandled error in client")
            break

        if not data: 
            print('unable to recieve from client')
            break 
        else:
            buffer.append(data)

            string_to_send = ''.join(x.decode('utf-8') for x in buffer)
            if string_to_send.find("\n") != -1:
                print(f"client len({len(string_to_send)}): {string_to_send}") 

                # clears buffer
                buffer = []
            
                # TODO: sends broadcast to others
                
                if string_to_send.strip() == "exit":
                    print("client issues exit command")

                    # TODO: sends client good bye and notify other connections
                    RemoveClient(client)
                    break
                elif string_to_send.strip() == "shutdown":
                    # uh oh!
                    print("someone shuts down the server")
                    try:
                        server_socket.shutdown(socket.SHUT_RDWR)                        
                    except:
                        # TODO: raise this error to main thread
                        server_socket.close()
                        print(f"unexpected error in shutdown command {sys.exc_info()}")
                    break

            # send back reversed string to client 
            # client.send("you said something".encode())
    
    # connection closed 
    print("thread exiting")
    client.close()    

client_threads = list()

# a 'set' of clients socket since a set can only contain unique values
client_sockets = list()

while True:
    try:
        # accept new connection
        new_client, client_address = server_socket.accept()
        print("connected from ", client_address)
        cli_thread = threading.Thread(target=HandleClient, args=(new_client,))
        client_threads.append(cli_thread)
        client_sockets.append(new_client)
        cli_thread.start()
    except:
        #print(f"unexpected error caught {sys.exc_info()}")
        print("unexpected error caught")
        if server_socket:
            server_socket.close()
        for index, client in enumerate(client_sockets):
            if client: 
                print(f"closing client {index}")
                client.close()
        break
    

# join all threads
for index, thread in enumerate(client_threads):
    print(f"Main : before joining thread {index}")
    thread.join()
    print(f"Main : thread {index} done")