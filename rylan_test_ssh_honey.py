# Import necessary modules
import logging  # For logging events
from logging.handlers import RotatingFileHandler  # For log rotation
import socket  # For creating network sockets
import paramiko  # Paramiko is used to implement SSH functionality
import threading  # For handling multiple clients with threads

# Constants
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"  # Custom SSH server banner shown to clients
host_key = paramiko.RSAKey(filename='server.key')  # Load the RSA private key for the SSH server

# --- Logging Setup ---

# Define the log format (only the message, no timestamps or log levels)
logging_format = logging.Formatter('%(message)s')

# Logger for connection attempts
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)  # Rotate after 2KB
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Logger for commands entered by clients
creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# --- Shell Emulator ---

# Simulate a basic shell to trick attackers
def emulated_shell(channel, client_ip):
    channel.send(b'corporate-jumpbox2$ ')  # Show a fake prompt
    command = b""
    
    while True:
        char = channel.recv(1)  # Read 1 byte at a time (user input)
        if not char:
            break
        channel.send(char)  # Echo back the character
        command += char
        
        if char == b'\r':  # Enter key pressed
            # Process entered command
            if command.strip() == b'exit':
                channel.send(b'\nGoodbye!\n')
                break
            elif command.strip() == b'pwd':
                channel.send(b"\n/usr/local\n")
            elif command.strip() == b'whoami':
                channel.send(b"\ncorpuser1\n")
            elif command.strip() == b'ls':
                channel.send(b"\njumpbox1.conf\n")
            elif command.strip() == b'cat jumpbox1.conf':
                channel.send(b"\nGo to cronus and subscribe.\n")
            else:
                # Echo unknown command
                channel.send(b"\n" + command.strip() + b"\n")

            # Log every command issued
            creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            
            # Reset prompt and command buffer
            channel.send(b'corporate-jumpbox2$ ')
            command = b""

# --- SSH Server Handler ---

# Defines how the SSH server behaves
class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()  # Event flag to track shell requests
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        # Accept session channels only
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"  # Only allow password-based authentication

    def check_auth_password(self, username, password):
        # Log authentication attempts
        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}') 

        # Check credentials if specified, otherwise accept all
        if self.input_username and self.input_password:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True  # Allow pseudo-terminal allocation

    def check_channel_shell_request(self, channel):
        self.event.set()  # Set event flag once shell is requested
        return True

# --- Connection Handler ---

# Function to handle each incoming client
def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")
    
    try:
        transport = paramiko.Transport(client)  # Create SSH transport over the socket
        transport.local_version = SSH_BANNER  # Set custom banner
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        transport.add_server_key(host_key)  # Supply host key
        transport.start_server(server=server)  # Start SSH session

        channel = transport.accept(100)  # Wait for client to open a channel
        if channel is None:
            print("No channel was opened.")
            return

        if not server.event.wait(10):  # Wait for shell request
            print("No shell request received.")
            return

        channel.send(b"Hello World!\n")  # Greet the user
        emulated_shell(channel, client_ip=client_ip)  # Start fake shell
    except Exception as error:
        print(f"Exception: {error}")
    finally:
        try:
            transport.close()
        except Exception as error:
            print(f"Error closing transport: {error}")

# --- Main Honeypot Listener ---

# Starts the SSH honeypot server
def honeypot(address, port, username, password):
    print(f"[-] Starting SSH Honeypot on {address}:{port}...", flush=True)

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
    socks.bind((address, port))  # Bind to address and port

    socks.listen(100)  # Start listening for incoming connections
    print(f"SSH server is listening on port {port}.", flush=True)
    print("Waiting for a client to connect...", flush=True)

    while True:
        try:
            client, addr = socks.accept()  # Accept a new connection
            print(f"Connection received from {addr[0]}:{addr[1]}", flush=True)

            # Create a new thread for each client
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(f"Error accepting connection: {error}", flush=True)

# Run honeypot on localhost and port 2223
honeypot('127.0.0.1', 2223, username=None, password=None)