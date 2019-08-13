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

def HandleClient(client): 
    
    # send welcome 
    client.send("welcome to this chatroom\n".encode())

    string_to_send = ''
    buffer = []

    # data received from client 
    while True:
        data = client.recv(1) 
        if not data: 
            print('unable to recieve from client') 
        else:
            print(data)
            buffer.append(data)

            string_to_send = ''.join(x.decode('utf-8') for x in buffer)
            if string_to_send.find("\n") != -1:
                print(f"client said: {string_to_send}") 

                # clears buffer
                buffer = []
            
                # TODO: sends broadcast to others
                
                if string_to_send.find("exit") != -1 and len(string_to_send) == 4:
                    print("client wants to exit")

                    # TODO: sends client good bye and notify other connections
                    break

            # send back reversed string to client 
            # client.send("you said something".encode())
    
    # connection closed 
    client.close()    

client_threads = list()

while True:
    try:
        # accept new connection
        new_client, client_address = server_socket.accept()
        print("connected from ", client_address)
        cli_thread = threading.Thread(target=HandleClient, args=(new_client,))
        client_threads.append(cli_thread)
        cli_thread.start()
    except KeyboardInterrupt:
        if new_client: 
            print("closing client")
            new_client.close()
        break

# join all threads
for index, thread in enumerate(client_threads):
    print("Main : before joining thread %d.", index)
    thread.join()
    print("Main : thread %d done", index)