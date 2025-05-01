# honeypy.py

# Import required modules
import argparse  # For parsing command-line arguments
from rylan_test_ssh_honey import *  # Import everything from your SSH honeypot module
from web_honeypot import *  # Import everything from your HTTP honeypot module

# Entry point of the script
if __name__ == "__main__":
    # Set up argument parser for command-line interface
    parser = argparse.ArgumentParser(description="HONEYPY - SSH/HTTP Honeypot Launcher")

    # Define command-line arguments
    parser.add_argument('-a', '--address', type=str, required=True, help="IP address to bind to")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port to bind to")
    parser.add_argument('-u', '--username', type=str, help="Username for SSH login")
    parser.add_argument('-pw', '--password', type=str, help="Password for SSH login")
    parser.add_argument('-s', '--ssh', action="store_true", help="Run SSH honeypot")  # Flag for SSH honeypot
    parser.add_argument('-w', '--http', action="store_true", help="Run HTTP honeypot")  # Flag for HTTP honeypot

    # Parse arguments
    args = parser.parse_args()

    # Print parsed arguments for confirmation
    print("✅ Parsed args:", args)

    try:
        # If SSH honeypot was selected
        if args.ssh:
            print("[-] Running SSH Honeypot...")

            # Launch SSH honeypot with provided credentials
            honeypot(args.address, args.port, args.username, args.password)

            # Fallback to None if not provided (though it's redundant here)
            if not args.username:
                username = None

            if not args.password:
                password = None

        # If HTTP honeypot was selected
        elif args.http:
            print("[-] Running HTTP WordPress Honeypot...")

            # Use default credentials if not supplied
            if not args.username:
                args.username = "admin"

            if not args.password:
                args.password = "password"

            # Show configured values
            print(f"Port: {args.port} Username: {args.username} Password {args.password}")

            # Launch HTTP honeypot
            run_web_honeypot(args.port, args.username, args.password)

        # If neither SSH nor HTTP honeypot was selected
        else:
            print("[!] Choose a honeypot type: SSH (--ssh) or HTTP (--http)")

    # Catch and display exceptions
    except Exception as e:
        print(f"\n[!] Exception occurred: {e}\nExiting HONEYPY...\n")