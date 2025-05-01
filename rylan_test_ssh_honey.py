import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading

# Constants
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"
host_key = paramiko.RSAKey(filename='server.key')  # Use your actual RSA key

# Logger setup
logging_format = logging.Formatter('%(message)s')

# Funnel Logger
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Creds Logger
creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# Emulated Shell
def emulated_shell(channel, client_ip):
    channel.send(b'corporate-jumpbox2$ ')
    command = b""
    
    while True:
        char = channel.recv(1)
        if not char:
            break
        channel.send(char)
        command += char
        
        if char == b'\r':  # Enter key pressed
            if command.strip() == b'exit':
                channel.send(b'\nGoodbye!\n')
                break
            elif command.strip() == b'pwd':
                channel.send(b"\n/usr/local\n")
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'whoami':
                channel.send(b"\ncorpuser1\n")
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'ls':
                channel.send(b"\njumpbox1.conf\n")
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                channel.send(b"\nGo to cronus and subscribe.\n")
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            else:
                channel.send(b"\n" + command.strip() + b"\n")
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            channel.send(b'corporate-jumpbox2$ ')
            command = b""

# SSH Server & Sockets
class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username: {username}, ' + f'password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}') 
        if self.input_username and self.input_password:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")
    
    try:
        transport = paramiko.Transport(client)  # Fix: pass client socket
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        # Supplies the host key
        transport.add_server_key(host_key)
        transport.start_server(server=server)

        # Waits for client to open a channel
        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")
            return

        if not server.event.wait(10):
            print("No shell request received.")
            return

        # Welcome message
        channel.send(b"Hello World!\n")
        emulated_shell(channel, client_ip=client_ip)
    except Exception as error:
        print(f"Exception: {error}")
    finally:
        try:
            transport.close()
        except Exception as error:
            print(f"Error closing transport: {error}")

# Provision SSH-based Honeypot

def honeypot(address, port, username, password):
    print(f"[-] Starting SSH Honeypot on {address}:{port}...", flush=True)
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"SSH server is listening on port {port}.", flush=True)

    # We only want to print the "waiting for client" message once.
    print("Waiting for a client to connect...", flush=True)

    while True:
        try:
            client, addr = socks.accept()
            print(f"Connection received from {addr[0]}:{addr[1]}", flush=True)

            # Spawn a new thread for the client
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(f"Error accepting connection: {error}", flush=True)


honeypot('127.0.0.1', 2223, username=None, password=None)