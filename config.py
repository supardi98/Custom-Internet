# config.py

CONFIG = {
    'MODE': 'sni_fronted',        #  direct | http_payload | sni_fronted
                                    #  default keeps today’s behaviour
    'FRONT_DOMAIN': 'aus.hackkcah.xyz',            #  used only in sni_fronted
    # The local port on which we will run a SOCKS proxy
    'LOCAL_SOCKS_PORT': 1080,

    # The intermediate HTTP proxy or WebSocket proxy you connect to
    'PROXY_HOST': 'api-prod.palmmerchant.com',
    'PROXY_PORT': 443,

    # The ultimate SSH server that lives behind the WS tunnel
    'TARGET_HOST': 'aus.hackkcah.xyz',
    'TARGET_PORT': 443,  # The WebSocket gateway port, not the direct SSH port

    # The raw SSH daemon behind the WebSocket tunnel might be on port 22,
    # but your WebSocket endpoint is 80. Typically, once the WS upgrade is done,
    # the traffic goes to SSH on the far side. We'll use Paramiko to speak SSH
    # across that raw connection.
    'SSH_USERNAME': '',
    'SSH_PASSWORD': '',
    'SSH_PORT': 443,  # The "internal" SSH port if needed by Paramiko handshake

    # The WebSocket handshake payload. This is the multi-step handshake
    # your proxy requires to upgrade to a raw TCP stream for SSH data.
    # Use [host] to be replaced by "TARGET_HOST:TARGET_PORT".
    # Use [crlf] for newlines.
    'PAYLOAD_TEMPLATE': (
        "GET / HTTP/1.1[crlf]Host: [host][crlf]Connection: Upgrade[crlf]Upgrade: websocket[crlf]"
        "Expect: 100-continue[crlf][crlf]"
    ),
}
