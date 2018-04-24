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
def initiate_tcp_server():
    print("Initiating TCP Server...")
    host, port = get_server_ip_and_port()
    addr = (host, port)
    TCP_SERVER.bind(addr)
    TCP_SERVER.listen(10)
    addr, port = TCP_SERVER.getsockname()
    print("New TCP server initialized on %s:%s" % (addr, port))

    try:
        Thread(target=handle_incoming_connections, args=(TCP_SERVER,)).start()
    except RuntimeError:
        print("TCP server couldn't spawn new connection handling thread")
        TCP_SERVER.close()


# This method kicks off the UDP server used to handle tcp messages coming from clients.
# Additionally this will spawn off a incoming connection thread handler.
def initiate_udp_server():
    print("Initiating UDP Server...")
    host, port = get_server_ip_and_port()
    addr = (host, port)
    UDP_SERVER.bind(addr)
    addr, port = UDP_SERVER.getsockname()
    print("New UDP server initialized on %s:%s" % (addr, port))

    try:
        Thread(target=handle_udp_message_received, args=(UDP_SERVER,)).start()
    except RuntimeError:
        print("UDP server couldn't spawn new connection handling thread")
        UDP_SERVER.close()


# This method is used to receive messages on UDP sockets and send it to all users.
def handle_udp_message_received(server):
    try:
        while True:
            msg, client_address = server.recvfrom(BUFFER_SIZE)
            addr, port = client_address

            print("New UDP message from %s:%s" % (addr, port))

            newUdpClient = False

            if port not in LISTENERS:
                UDP_SERVER.sendto("<<<CONNECTED via UDP>>>", (addr, port))
                LISTENERS[port] = client_address
                newUdpClient = True

            first_bracket_index = msg.find('>')
            user_portion = msg[12:]
            name = user_portion[:+first_bracket_index - 12]
            halfWayNewMsg = msg[first_bracket_index + 10:]
            newMsg = halfWayNewMsg[:-3]

            if '<<<EXIT>>>' not in msg:

                if newUdpClient:
                    newMsg = "Connected"

                user_msg = str(name)+"(UDP): " + str(newMsg)
                send_all(user_msg)
            else:
                server.sendto('<<<EXITED>>>', (addr, port))
                del LISTENERS[port]
                left_msg = set_encoding("LEFT", name)
                send_all(left_msg)
                break

    except socket.error:
        print("Could not handle UDP messaging")


# This method will loop endlessly while it awaits clients to connect to its socket. When it does register the client
# it will send it back a connected keyword, and then spawn off another thread to handle the new client.
def handle_incoming_connections(server):
    while True:
        client_socket, client_address = server.accept()
        print("New TCP connection from %s" % str(client_address))
        client_socket.send("<<<CONNECTED via TCP>>>")

        # De_encodes names to be used as a variable
        msg = client_socket.recv(BUFFER_SIZE);

        first_bracket_index = msg.find('>')
        user_portion = msg[12:]
        name = user_portion[:+first_bracket_index - 12]
        msg = name + "(TCP): Connected"
        send_all(msg)

        Thread(target=handle_client_connection, args=(client_socket, name)).start()


# This function is used to handle TCP client messages and send it to all connected users.
def handle_client_connection(client, name):
    client_name = name
    CLIENTS[client_name] = client

    try:
        while True:
            msg = client.recv(BUFFER_SIZE)

            first_bracket_index = msg.find('>')
            user_portion = msg[12:]
            name = user_portion[:+first_bracket_index - 12]
            halfWayNewMsg = msg[first_bracket_index + 10:]
            newMsg = halfWayNewMsg[:-3]

            if '<<<EXIT>>>' not in msg:
                # attach new_message encoding with user message
                user_msg = str(name) + "(TCP): " + str(newMsg)
                send_all(user_msg)
            else:
                client.send("<<<EXITED>>>")
                client.close()
                del CLIENTS[name]

                left_msg = set_encoding("LEFT", name)
                send_all(left_msg)
                break
    except socket.error:
        del CLIENTS[client_name]
        send_all(client_name + " disconnected")
        print("Client Disconnected")


# This function is responsible for sending all clients regardless of their protocol the new message.
def send_all(msg):
    if (len(CLIENTS) > 0):
        print('Sending all TCP clients %s ' % msg)
        for name in CLIENTS:
            print('Sending to %s:%s via TCP' % (CLIENTS[name].getpeername()));
            CLIENTS[name].send(str(msg))

    if (len(LISTENERS) >0):
        print('Sending all UDP clients %s ' % msg)
        for port in LISTENERS:
            print('Sending to %s:%s via UDP' % (LISTENERS[port][0], port))
            UDP_SERVER.sendto(str(msg), LISTENERS[port])


# Function To Handle the Delimiter using Regex
def de_encode(encoded_msg):
    result = re.findall('<<<(.*?)>>>', encoded_msg)
    return result


# Used for encoding messages sent to the client
# Identifiers are used to communicate messages, userlists, and events
# between the backend and front-end
def set_encoding(key_identifer, encoded_msg):
    result = "<<<" + key_identifer + ">>>" + "<<<" + encoded_msg + ">>>"
    return result


def main(TCP_SERVER, UDP_SERVER):
    print("To close out of this server press Control + Z\n")
    try:
        initiate_tcp_server()
    except IOError:
        print("TCP Server encountered an IOError")
        TCP_SERVER.close()
        TCP_SERVER = None

    try:
        initiate_udp_server()
    except IOError:
        print("UDP Server encountered an IOError")
        UDP_SERVER.close()
        UDP_SERVER = None

TCP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CLIENTS = {}
LISTENERS = {}
BUFFER_SIZE = 1024


if __name__ == "__main__":
    main(TCP_SERVER, UDP_SERVER)
