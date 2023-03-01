import socket
import threading

SERVER_HOST = '127.0.0.1'  # change this to your server IP address, or keep to run in your local network only
SERVER_PORT = 8000
MAX_CLIENTS = 10
MAX_USERNAME_LEN = 12


def broadcast(message, client_socket):
    """
    Send a message to all clients in the chatroom, except for the client who sent the message.
    """
    for sock in clients:
        if sock != server_socket and sock != client_socket:
            try:
                sock.send(message)
            except:
                print("Error broadcasting message")


def handle_client(client_socket, client_address):
    """
    Handle messages from a single client.
    """
    # Ask the client to choose a username
    client_socket.send(b"Enter a username (up to 12 characters): ")

    # Receive the username one byte at a time until a newline character is received
    username_bytes = bytearray()
    while True:
        b = client_socket.recv(1)
        if b == b'\n':
            break
        username_bytes += b

    # Decode the username bytes and truncate to maximum length
    username = username_bytes.decode().strip()[:MAX_USERNAME_LEN]

    # Add the client to the list of clients
    clients.append(client_socket)

    # Broadcast a welcome message to all clients
    welcome_message = f"{username} has joined the chatroom!\n".encode()
    broadcast(welcome_message, client_socket)

    while True:
        try:
            # Receive messages from the client
            message = client_socket.recv(1024)
            if message:
                # Wait for the user to press Enter before broadcasting the message
                while message[-1] != 10:
                    message += client_socket.recv(1024)
                # Broadcast the message to all clients
                broadcast(f"{username}: {message.decode()}".encode(), client_socket)
            else:
                # If the client has disconnected, remove them from the list of clients and broadcast a goodbye message
                clients.remove(client_socket)
                client_socket.close()
                goodbye_message = f"{username} has left the chatroom.\n".encode()
                broadcast(goodbye_message, client_socket)
                break
        except:
            continue


def start_server():
    """
    Start the server and listen for incoming connections.
    """
    global server_socket, clients

    # Create the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to a specific address and port
    server_socket.bind((SERVER_HOST, SERVER_PORT))

    # Listen for incoming connections
    server_socket.listen(MAX_CLIENTS)

    # Create an empty list of clients
    clients = []

    print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        # Accept incoming connections
        client_socket, client_address = server_socket.accept()

        # Handle the connection in a new thread
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()


def main():
    """
    Main function to start the server.
    """
    start_server()


if __name__ == '__main__':
    main()
