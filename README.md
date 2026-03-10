# CUSTOM FREEDOM INTERNET TOOL (CFIT - Custom-Internet)
free-internet tool. For all.
## SSH-over-WebSocket with SOCKS Proxy (Supports payloads & SNI fronting)

This project demonstrates tunneling SSH through a WebSocket “proxy” endpoint, then exposing a local SOCKS4/5 proxy. Applications can connect to `127.0.0.1:1080` (by default), and all traffic is forwarded over SSH via a remote WebSocket gateway. It now supports three tunnel modes (direct, HTTP payload, and SNI domain fronting) for maximum flexibility.

## Features

- **WebSocket Handshake**: Performs a custom HTTP/WebSocket handshake with a proxy (`ws_tunnel.py`).
- **SSH-over-WebSocket**: Uses Paramiko to authenticate to a remote SSH server once the tunnel is established.
- **Local SOCKS Proxy**: Exposes a SOCKS4/5 listener on your local machine. All incoming connections route through SSH.
- **Flexible Tunnel Modes**: Choose between:
  - **direct**: Plain TCP straight to target
  - **http_payload**: Plain TCP to proxy+custom upgrade payload
  - **sni_fronted**: TLS to proxy with SNI domain fronting, then upgrade payload

## How It Works

1. **Strategy Selection**: Based on `MODE` in `config.yaml`, the script establishes a raw connection (TCP or TLS) to the proxy.
2. **WebSocket Handshake**: `ws_tunnel.py` performs the HTTP/WebSocket upgrade handshake.
3. **Local SSH Bridge**: `bridge_connector.py` creates a local TCP listener (port 2222 by default) that pipes data into the established WebSocket tunnel.
4. **Automated SSH Client**: `main.py` launches a system `ssh` command using `sshpass` to authenticate. It connects to the local bridge and creates a **SOCKS5 Proxy** on the configured port.


## Project Structure

```
.
├── config.py            # Configuration (hosts, ports, credentials, mode, front domain)
├── .gitignore
├── main.py              # Entry point: selects strategy, sets up tunnel, starts SSH & SOCKS
├── project_dump.txt     # Example data or logs
├── README.md            # (This file)
├── ssh_connector.py     # SSHTransport + SOCKS server implementation
├── ws_tunnel.py         # HTTP/WebSocket handshake & raw socket creation
└── tunnel_strategies.py # Strategy pattern for direct/http_payload/sni_fronted
```

## Configuration

User-configurable values are now managed in **`config.yaml`**. 

```yaml
MODE: "sni_fronted"             # direct | http_payload | sni_fronted
FRONT_DOMAIN: "example.com"     # used only in sni_fronted

LOCAL_SOCKS_PORT: 1080          # The SOCKS5 proxy port for your browser/apps
LOCAL_BRIDGE_PORT: 2222         # Internal bridge port (don't conflict)

PROXY_HOST: "your.proxy.com"    # WebSocket/HTTP proxy endpoint
PROXY_PORT: 443

TARGET_HOST: "ssh-ws.com"       # The SSH-over-WS gateway
TARGET_PORT: 443

SSH_USERNAME: "your_user"
SSH_PASSWORD: "your_password"

PAYLOAD_TEMPLATE: "GET / HTTP/1.1[crlf]Host: [host][crlf]Upgrade: websocket[crlf][crlf]"
```

| Key | Description |
|-----|-------------|
| `MODE` | `direct`, `http_payload`, or `sni_fronted`. |
| `FRONT_DOMAIN` | SNI used in `sni_fronted` mode. |
| `LOCAL_SOCKS_PORT` | The port you will use in your browser/app (default 1080). |
| `LOCAL_BRIDGE_PORT` | Port for the local TCP bridge (default 2222). |
| `PROXY_HOST` | The hostname/IP of the proxy server. |
| `TARGET_HOST` | The destination SSH WebSocket gateway. |
| `SSH_USERNAME` | Your SSH account username. |
| `SSH_PASSWORD` | Your SSH account password. |
| `PAYLOAD_TEMPLATE` | Custom WebSocket handshake payload. |

## Installation & Dependencies

### 1. System Packages

This tool requires `openssh-client` and `sshpass` to handle the SSH connection and SOCKS tunneling.

**Ubuntu / Debian / Linux Mint:**
```bash
sudo apt update
sudo apt install python3 python3-pip openssh-client sshpass -y
```

**Termux (Android):**
```bash
pkg update
pkg install python openssh sshpass -y
```

### 2. Python Dependencies

The project uses `PyYAML` to load configuration from `config.yaml`.

```bash
pip install pyyaml
```

*(Note: While `paramiko` is included in the project files as an alternative, the default `main.py` flow uses the system `ssh` command.)*

## Usage

1. **Configure**: Edit **`config.yaml`** with the correct hosts, ports, credentials, and `MODE`.
2. **Run**:
   ```bash
   python main.py
   ```
3. **Use the SOCKS Proxy**: Once running, you’ll see:
   ```
   [*] Starting in mode: sni_fronted
   [*] WebSocket handshake done. Returning raw socket.
   [*] Bridge listening on 127.0.0.1:2222
   [*] Launching SSH Client (SOCKS5 on port 1080)...
   [SUCCESS] Tunnel & SOCKS5 Proxy AKTIF!
   [INFO] Gunakan SOCKS5 -> 127.0.0.1:1080 in your browser/app.
   ```
   - Configure your application or browser to use **SOCKS5** at `127.0.0.1:1080`.

## Tor/Browser Configuration

If you want to route Tor through this SOCKS proxy:

1. Start this program first.
2. In Tor Browser settings → Network, set a custom proxy:
   - **SOCKS5**
   - Address: `127.0.0.1`
   - Port: `1080`

The enhanced SOCKS4/5 logic in `ssh_connector.py` handles DNS and domain lookups properly.

## Troubleshooting

- **Authentication Failure**: Verify your SSH credentials or server settings.
- **Handshake Fails**: Ensure your `PAYLOAD_TEMPLATE` matches the proxy’s requirements, and check console output for HTTP response details.
- **Connection Refused**: Confirm access to the proxy and gateway (e.g., port 443/TLS vs. port 80).
- **Timeout or No Data**: Check firewall/NAT rules and any advanced handshake needs.

## Contributing

1. Fork the repo  
2. Make changes / add features (e.g. new `TunnelStrategy`)  
3. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).