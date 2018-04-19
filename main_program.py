"""main program to initiate the servers that we care about """

from threading import Thread

import socket
import re


def get_server_ip_and_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    addr, port = s.getsockname()
    s.close()
    return (addr, port)


def initiate_tcp_server(server):
    print("Initiating TCP Server...")
    host, port = get_server_ip_and_port()
    addr = (host, port)
    server.bind(addr)
    server.listen(10)
    addr, port = server.getsockname()
    print("New TCP server initialized on %s:%s" % (addr, port))

    try:
        Thread(target=handle_incoming_connections, args=(server,)).start()
    except RuntimeError:
        server.close()
        server = None


def handle_client_connection(client):
    # De_encodes names to be used as a variable
    name = str(de_encode(client.recv(BUFFER_SIZE).decode("utf8"))[1])
    msg = set_encoding("NEW_USER",name + " connected" )
    send_all(msg)

    CLIENTS[client] = name
    try:
        while True:
            msg = client.recv(BUFFER_SIZE)
            if msg != "<<<EXIT>>>":
                #  attach new_message encoding with user message
                user_msg = set_encoding("NEW_MESSAGE",str(name)+": "+str(msg))
                send_all(user_msg)
            else:
                client.send("<<<EXITED>>>")
                client.close()
                del CLIENTS[client]
                left_msg = set_encoding("LEFT",name)
                send_all(left_msg)
                break
    except socket.error:
        print("Client Disconnected")


def send_all(msg):
    for client_socket in CLIENTS:
        client_socket.send(str(msg))



def handle_incoming_connections(server):
    while True:
        client_socket, client_address = server.accept()
        print("New connection from %s" % str(client_address))
        client_socket.send("<<<CONNECTED>>>")
        Thread(target=handle_client_connection, args=(client_socket,)).start()

# Function To Handle the Delimiter using Regex
def de_encode(encoded_msg):
    result = re.findall('<<<(.*?)>>>',encoded_msg)
    return result


# Used for encoding messages sent to the client
# Identifiers are used to communicate messages, userlists, and events
# between the backend and front-end
def set_encoding(key_identifer,encoded_msg):
    result = "<<<" + key_identifer + ">>>" + "<<<" + encoded_msg + ">>>"
    return result




CLIENTS = {}
TCP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
BUFFER_SIZE = 1024


if __name__ == "__main__":
    try:
        initiate_tcp_server(TCP_SERVER)
    except IOError:
        TCP_SERVER.close()
        TCP_SERVER = None
