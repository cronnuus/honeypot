# honeypy.py

import argparse
from rylan_test_ssh_honey import *
from web_honeypot import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HONEYPY - SSH/HTTP Honeypot Launcher")

    parser.add_argument('-a', '--address', type=str, required=True, help="IP address to bind to")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port to bind to")
    parser.add_argument('-u', '--username', type=str, help="Username for SSH login")
    parser.add_argument('-pw', '--password', type=str, help="Password for SSH login")

    parser.add_argument('-s', '--ssh', action="store_true", help="Run SSH honeypot")
    parser.add_argument('-w', '--http', action="store_true", help="Run HTTP honeypot")

    args = parser.parse_args()

    print("✅ Parsed args:", args)

    try:
        if args.ssh:
            print("[-] Running SSH Honeypot...")
            honeypot(args.address, args.port, args.username, args.password)

            if not args.username:
                username = None

            if not args.password:
                password = None

        elif args.http:
            print("[-] Running HTTP WordPress Honeypot...")

            if not args.username:
                args.username = "admin"

            if not args.password:
                args.password = "password"

            print(f"Port: {args.port} Username: {args.username} Password {args.password}")
            run_web_honeypot(args.port, args.username, args.password)

            pass
        else:
            print("[!] Choose a honeypot type: SSH (--ssh) or HTTP (--http)")

    except Exception as e:
        print(f"\n[!] Exception occurred: {e}\nExiting HONEYPY...\n")
