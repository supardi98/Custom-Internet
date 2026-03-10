import socket
import threading

class SSHBridge:
    """
    Acts as a simple TCP bridge:
    Local Port (e.g. 2222) -> [TUNNEL] -> Remote SSH Server
    
    This avoids using Paramiko/Cryptography in Python.
    The user connects via standard 'ssh -p 2222 user@localhost'.
    """

    def __init__(self, ws_socket):
        """
        ws_socket: the raw connected socket from the WS tunnel
        """
        self.ws_socket = ws_socket
        self.server_socket = None

    def start_bridge(self, local_port):
        """
        Start a local TCP server that forwards all traffic to ws_socket.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', local_port))
        self.server_socket.listen(1)
        
        print(f"[*] Bridge listening on 127.0.0.1:{local_port}")
        print(f"[*] Connect using: ssh -D 1080 -p {local_port} [user]@127.0.0.1")

        def handle_client(client_sock):
            # Forward data bidirectionally
            t1 = threading.Thread(target=self._forward, args=(client_sock, self.ws_socket))
            t2 = threading.Thread(target=self._forward, args=(self.ws_socket, client_sock))
            t1.start()
            t2.start()

        def accept_loop():
            # In bridge mode, we typically only handle ONE SSH session at a time
            # because the ws_socket is a single connection to the remote SSH port.
            try:
                client_sock, addr = self.server_socket.accept()
                print(f"[*] SSH Client connected from {addr}")
                handle_client(client_sock)
            except Exception as e:
                print(f"[!] Bridge error: {e}")

        threading.Thread(target=accept_loop, daemon=True).start()

    def _forward(self, src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass
        finally:
            src.close()
            dst.close()

def start_ssh_bridge(ws_socket, local_port):
    bridge = SSHBridge(ws_socket)
    bridge.start_bridge(local_port)
    return bridge
