# main.py

import sys
import time
import subprocess
import signal
from config import CONFIG
from tunnel_strategies import get_strategy
from bridge_connector import start_ssh_bridge

def run():
    auto_reconnect = CONFIG.get('AUTO_RECONNECT', True)
    reconnect_interval = CONFIG.get('RECONNECT_INTERVAL', 5)
    
    while True:
        ssh_process = None
        try:
            mode = CONFIG.get('MODE', 'sni_fronted')
            strategy_cls = get_strategy(mode)
            
            print(f"[*] Starting in mode: {mode}")
            
            # 1. Establish the underlying tunnel (WebSocket/SNI)
            ws_sock = strategy_cls(CONFIG).establish()
            
            # 2. Start the local bridge
            bridge_host = CONFIG.get('LOCAL_BRIDGE_HOST', '127.0.0.1')
            bridge_port = CONFIG.get('LOCAL_BRIDGE_PORT', 2222)
            max_dl = CONFIG.get('MAX_DOWNLOAD_SPEED', 0)
            max_ul = CONFIG.get('MAX_UPLOAD_SPEED', 0)
            start_ssh_bridge(ws_sock, bridge_port, local_host=bridge_host, max_download=max_dl, max_upload=max_ul)

            # 3. Automation: Prepare SSH variables
            ssh_user = CONFIG.get('SSH_USERNAME', 'root')
            ssh_pass = CONFIG.get('SSH_PASSWORD', '')
            socks_host = CONFIG.get('LOCAL_SOCKS_HOST', '127.0.0.1')
            socks_port = CONFIG.get('LOCAL_SOCKS_PORT', 1080)

            # Tunggu sebentar agar port bridge benar-benar siap
            time.sleep(1)

            # Perintah SSH Otomatis
            # Using -D socks_host:socks_port to allow shared proxy if host is 0.0.0.0
            cmd = [
                "sshpass", "-p", ssh_pass,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-D", f"{socks_host}:{socks_port}",
                "-p", str(bridge_port),
                "-N",
                f"{ssh_user}@{bridge_host}"
            ]


            print(f"[*] Launching SSH Client (SOCKS5 on {socks_host}:{socks_port})...")

            # Jalankan SSH di background
            ssh_process = subprocess.Popen(cmd)

            print("-" * 50)
            print(f"[SUCCESS] Tunnel & SOCKS5 Proxy AKTIF!")
            print(f"[INFO] Gunakan SOCKS5 -> {socks_host}:{socks_port}")
            print("-" * 50)

            print("[*] Tekan CTRL+C untuk berhenti.")
            
            # Loop utama untuk menjaga script tetap jalan
            while True:
                # Cek apakah proses SSH masih hidup
                if ssh_process.poll() is not None:
                    print("[!] SSH Client terputus.")
                    break
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n[!] Menutup koneksi...")
            if ssh_process:
                ssh_process.terminate()
            break
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            # Cleanup: Matikan proses SSH jika masih jalan
            if ssh_process and ssh_process.poll() is None:
                ssh_process.terminate()
                print("[*] SSH Client dihentikan.")
        
        if not auto_reconnect:
            break
            
        print(f"[*] Mencoba menyambung kembali dalam {reconnect_interval} detik...")
        time.sleep(reconnect_interval)

    sys.exit(0)

if __name__ == "__main__":
    run()
