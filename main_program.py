"""Main program that initiates a UDP and TCP server to handle client communications"""


from threading import Thread
import socket
import re


# Dynamically get a unique port and server IP.
def get_server_ip_and_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    addr, port = s.getsockname()
    s.close()
    return (addr, port)


# This method kicks off the TCP server used to handle tcp messages coming from clients.
# Additionally this will spawn off a incoming connection thread handler.
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
        print("TCP server couldn't spawn new connection handling thread")
        server.close()
        server = None


# This method kicks off the UDP server used to handle tcp messages coming from clients.
# Additionally this will spawn off a incoming connection thread handler.
def initiate_udp_server(server):
    print("Initiating UDP Server...")
    host, port = get_server_ip_and_port()
    addr = (host, port)
    server.bind(addr)
    addr, port = server.getsockname()
    print("New UDP server initialized on %s:%s" % (addr, port))

    try:
        Thread(target=handle_incoming_udp_message, args=(server,)).start()
    except RuntimeError:
        print("UDP server couldn't spawn new connection handling thread")
        server.close()
        server = None


def handle_incoming_udp_message(server):
    while True:
        client_data, client_address = server.recvfrom(BUFFER_SIZE)
        Thread(target=handle_udp_message_received, args=(client_data, client_address,)).start()


def handle_udp_message_received(server, client_data, client_address):
    client_port = client_data[:5]
    print("New message from %s:%s" % client_address, client_port)
    print("client data: %s" % client_data)
    LISTENERS[client_port] = client_address


# This method will loop endlessly while it awaits clients to connect to its socket. When it does register the client
# it will send it back a connected keyword, and then spawn off another thread to handle the new client.
def handle_incoming_connections(server):
    while True:
        client_socket, client_address = server.accept()
        print("New connection from %s" % str(client_address))
        client_socket.send("<<<CONNECTED>>>")
        Thread(target=handle_client_connection, args=(client_socket,)).start()


# This function is used
def handle_client_connection(client):
    # De_encodes names to be used as a variable
    name = str(de_encode(client.recv(BUFFER_SIZE).decode("utf8"))[1])
    msg = set_encoding("NEW_USER", name + " connected" )
    send_all(msg)

    CLIENTS[client] = name
    LISTENERS[client.getsockname[1]] = client.getsockname[0]

    try:
        while True:
            msg = client.recv(BUFFER_SIZE)
            if msg != "<<<EXIT>>>":
                # attach new_message encoding with user message
                user_msg = set_encoding("NEW_MESSAGE", str(name)+": "+str(msg))
                send_all(user_msg)
            else:
                client.send("<<<EXITED>>>")
                client.close()
                del CLIENTS[client]
                del LISTENERS[client.getsockname[1]]

                left_msg = set_encoding("LEFT", name)
                send_all(left_msg)
                break
    except socket.error:
        print("Client Disconnected via error")


# This function is responsible for sending all clients regardless of their protocol the new message.
def send_all(msg, server):
    for client_socket in CLIENTS:
        client_socket.send(str(msg))

    if (server):
        for listener in LISTENERS:
            server.sendto(msg, listener)


# Function To Handle the Delimiter using Regex
def de_encode(encoded_msg):
    result = re.findall('<<<(.*?)>>>',encoded_msg)
    return result


# Used for encoding messages sent to the client
# Identifiers are used to communicate messages, userlists, and events
# between the backend and front-end
def set_encoding(key_identifer, encoded_msg):
    result = "<<<" + key_identifer + ">>>" + "<<<" + encoded_msg + ">>>"
    return result


CLIENTS = {}
LISTENERS = {}
TCP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BUFFER_SIZE = 1024


if __name__ == "__main__":
    try:
        initiate_tcp_server(TCP_SERVER)
    except IOError:
        print("TCP Server encountered an IOError")
        TCP_SERVER.close()
        TCP_SERVER = None

    initiate_udp_server(UDP_SERVER)

    # try:
    #     initiate_udp_server(UDP_SERVER)
    # except IOError:
    #     print("UDP Server encountered an IOError")
    #     UDP_SERVER.close()
    #     UDP_SERVER = None

