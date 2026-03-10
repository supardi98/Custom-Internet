import socket
import threading
import time

class SSHBridge:
    """
    Acts as a simple TCP bridge:
    Local Port (e.g. 2222) -> [TUNNEL] -> Remote SSH Server
    
    This avoids using Paramiko/Cryptography in Python.
    The user connects via standard 'ssh -p 2222 user@localhost'.
    """

    def __init__(self, ws_socket, max_download=0, max_upload=0):
        """
        ws_socket: the raw connected socket from the WS tunnel
        max_download: Max download speed in KB/s (0 = unlimited)
        max_upload: Max upload speed in KB/s (0 = unlimited)
        """
        self.ws_socket = ws_socket
        self.server_socket = None
        self.max_download = max_download * 1024 # Convert to bytes
        self.max_upload = max_upload * 1024     # Convert to bytes

    def start_bridge(self, local_port, local_host='127.0.0.1'):
        """
        Start a local TCP server that forwards all traffic to ws_socket.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((local_host, local_port))
        self.server_socket.listen(1)
        
        print(f"[*] Bridge listening on {local_host}:{local_port}")
        if self.max_download > 0 or self.max_upload > 0:
            dl_str = f"{self.max_download//1024} KB/s" if self.max_download > 0 else "Unlimited"
            ul_str = f"{self.max_upload//1024} KB/s" if self.max_upload > 0 else "Unlimited"
            print(f"[*] Speed Limits - Download: {dl_str}, Upload: {ul_str}")

        def handle_client(client_sock):
            # Forward data bidirectionally
            # Upload: client -> ws_socket
            t1 = threading.Thread(target=self._forward, args=(client_sock, self.ws_socket, self.max_upload))
            # Download: ws_socket -> client
            t2 = threading.Thread(target=self._forward, args=(self.ws_socket, client_sock, self.max_download))
            t1.start()
            t2.start()

        def accept_loop():
            try:
                client_sock, addr = self.server_socket.accept()
                print(f"[*] SSH Client connected from {addr}")
                handle_client(client_sock)
            except Exception as e:
                print(f"[!] Bridge error: {e}")

        threading.Thread(target=accept_loop, daemon=True).start()

    def _forward(self, src, dst, rate_limit):
        """
        src: Source socket
        dst: Destination socket
        rate_limit: Max bytes per second (0 = unlimited)
        """
        try:
            start_time = time.time()
            total_bytes = 0
            
            while True:
                data = src.recv(4096)
                if not data:
                    break
                
                dst.sendall(data)
                
                if rate_limit > 0:
                    total_bytes += len(data)
                    elapsed = time.time() - start_time
                    expected_time = total_bytes / rate_limit
                    
                    if elapsed < expected_time:
                        time.sleep(expected_time - elapsed)
                    
                    # Reset counter periodically to avoid floating point drift or very large numbers
                    if total_bytes > rate_limit * 5: # reset every 5 seconds worth of data
                        start_time = time.time()
                        total_bytes = 0

        except:
            pass
        finally:
            src.close()
            dst.close()

def start_ssh_bridge(ws_socket, local_port, local_host='127.0.0.1', max_download=0, max_upload=0):
    bridge = SSHBridge(ws_socket, max_download, max_upload)
    bridge.start_bridge(local_port, local_host)
    return bridge
