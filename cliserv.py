#!/user/bin/env python

import socket
import threading
import argparse
import signal
import sys

# Standard multi-threaded server.
# Simple TCP/UDP client to test services, fuzzing, send data, etc.


# Help for arguments.
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--service",
        dest="service",
        help="Enter tcp or udp for type of client, or serv for server",
    )
    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        help="Enter the ip address or domain of client or server",
    )
    parser.add_argument("-p", "--port", dest="port", help="Enter the PORT")
    args = parser.parse_args()
    if not args.service:
        parser.error(
            "[*] Specify the service with -s or --service. Use --help or -h for more info."
        )
    elif not args.target:
        parser.error(
            "[*] Specify the target with -t or --target. Use --help or -h for more info."
        )
    elif not args.port:
        parser.error(
            "[*] Specify the port with -p or --port. Use --help or -h for more info."
        )
    return args


opt = get_arguments()
service = opt.service
target = str(opt.target)
port = int(opt.port)


def run_service(stype):
    if stype == "serv":
        server(target, port)
    elif stype == "tcp":
        run_tcpclient(target, port)
    elif stype == "udp":
        run_udpclient(target, port)


def run_tcpclient(dom, por):
    # Create socket object (with IPv4, TCP) saving it in client.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the client to the server.
    client.connect((dom, por))

    # Send some data as bytes (set up as argument).
    data = f"GET / HTTP/1.1\r\nHost: {dom}\r\n\r\n"
    data_bytes = bytes(data, "utf8")
    # client.send(b"GET / HTTP/1.1\r\nHost: domain.com\r\n\r\n")
    client.send(data_bytes)

    # Receive the data, print the data and close the socket.
    response = client.recv(4096)
    print(response.decode())
    client.close()


def run_udpclient(tar, por):
    # Create socket object (with IPv4, TCP) saving it in client.
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind socket to the target.
    client.bind((tar, por))
    # Send some data as bytes.
    data = f"HERE IS SOME DATA FOR {tar}:{por}"
    #data_bytes = bytes(data)
    data_bytes = data.encode("utf-8")
    client.sendto(data_bytes, (tar, por))

    # Receive the data and remote info, print the data and close the socket.
    res, addr = client.recvfrom(4096)
    print(res.decode())
    client.close()


def server(IP, PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the address and port to listen on.
    server.bind((IP, PORT))
    # Listen with the maximum backlog of connections at 5.
    server.listen(5)
    print(f"[*] Listening on {IP}:{PORT}")

    while True:
        # Save the client socket in client variable.
        # Save the remote connection in address variable.
        client, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        # Create a new thread object that points to client_handler, passing the client socket object.
        client_thread = threading.Thread(target=client_handler, args=(client,))
        # Start thread that handles the client connection and begin the server loop.
        client_thread.start()


def client_handler(client_socket):
    with client_socket as sock:
        # Receive and send message to client.
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b"ACK")


def signal_handler(sig, frame):
    print("\n[+] Server shutdown with Ctrl-c. Exiting now....")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    run_service(service)
