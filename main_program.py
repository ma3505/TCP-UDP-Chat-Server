"""main program to initiate the servers that we care about """

from threading import Thread
import socket

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
    name = client.recv(BUFFER_SIZE).decode("utf8")
    send_all("<<<NEW>>>:%s" % name, name)
    CLIENTS[client] = name

    while True:
        msg = client.recv(BUFFER_SIZE)
        if msg != "<<<EXIT>>>":
            send_all(msg, name)
        else:
            client.send("<<<EXITED>>>")
            client.close()
            del CLIENTS[client]
            send_all("<<<LEFT>>>:%s" % name, name)
            break

def send_all(msg, name):
    for client_socket in CLIENTS:
        client_socket.send("<<<FROM>>>:%s <<<|||>>> %s" % name, msg)


def handle_incoming_connections(server):
    while True:
        client_socket, client_address = server.accept()
        print("New connection from %s" % client_address)
        client_socket.send("<<<CONNECTED>>>")
        Thread(target=handle_client_connection, args=(client_socket,)).start()


CLIENTS = {}
TCP_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
BUFFER_SIZE = 1024


if __name__ == "__main__":
    try:
        initiate_tcp_server(TCP_SERVER)
    except IOError:
        TCP_SERVER.close()
        TCP_SERVER = None
