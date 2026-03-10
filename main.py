# main.py

import sys
import time
import subprocess
import signal
from config import CONFIG
from tunnel_strategies import get_strategy
from bridge_connector import start_ssh_bridge

def run():
    ssh_process = None
    try:
        mode = CONFIG.get('MODE', 'sni_fronted')
        strategy_cls = get_strategy(mode)
        
        print(f"[*] Starting in mode: {mode}")
        
        # 1. Establish the underlying tunnel (WebSocket/SNI)
        ws_sock = strategy_cls(CONFIG).establish()
        
        # 2. Start the local bridge
        bridge_port = CONFIG.get('LOCAL_BRIDGE_PORT', 2222)
        start_ssh_bridge(ws_sock, bridge_port)
        
        # 3. Automation: Prepare SSH variables
        ssh_user = CONFIG.get('SSH_USERNAME', 'root')
        ssh_pass = CONFIG.get('SSH_PASSWORD', '')
        socks_port = CONFIG.get('LOCAL_SOCKS_PORT', 1080)
        
        # Tunggu sebentar agar port bridge benar-benar siap
        time.sleep(1)

        # Perintah SSH Otomatis
        # -N: Do not execute a remote command (hanya untuk tunneling)
        # -f: Go to background (tapi kita handle via subprocess saja)
        cmd = [
            "sshpass", "-p", ssh_pass,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-D", str(socks_port),
            "-p", str(bridge_port),
            "-N", # Penting: Agar SSH hanya fokus buat tunnel SOCKS saja
            f"{ssh_user}@127.0.0.1"
        ]
        
        print(f"[*] Launching SSH Client (SOCKS5 on port {socks_port})...")
        
        # Jalankan SSH di background
        ssh_process = subprocess.Popen(cmd)
        
        print("-" * 50)
        print(f"[SUCCESS] Tunnel & SOCKS5 Proxy AKTIF!")
        print(f"[INFO] Gunakan SOCKS5 -> 127.0.0.1:{socks_port} di HP Anda.")
        print("-" * 50)
        print("[*] Tekan CTRL+C untuk berhenti.")
        
        # Loop utama untuk menjaga script tetap jalan
        while True:
            # Cek apakah proses SSH masih hidup
            if ssh_process.poll() is not None:
                print("[!] SSH Client terputus. Mencoba berhenti...")
                break
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[!] Menutup koneksi...")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # Cleanup: Matikan proses SSH jika masih jalan
        if ssh_process:
            ssh_process.terminate()
            print("[*] SSH Client dihentikan.")
        sys.exit(0)

if __name__ == "__main__":
    run()
