
import sys
import os
import socket
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Load .env
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

from backend.config import settings
import smtplib

def diagnostic():
    print("--- SMTP Connectivity Diagnostic ---")
    hosts = ["smtp.gmail.com", "smtp-relay.gmail.com", "74.125.142.108"] # Google SMTP IPs
    ports = [465, 587]
    
    for host in hosts:
        for port in ports:
            print(f"\nTesting {host}:{port}...")
            try:
                # Check DNS first
                try:
                    ip = socket.gethostbyname(host)
                    print(f"  DNS Resolved: {ip}")
                except Exception as dns_e:
                    print(f"  DNS Resolution Failed: {dns_e}")
                    continue

                # Try to open a socket
                print(f"  Attempting socket connection to {host}:{port}...")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                result = s.connect_ex((host, port))
                if result == 0:
                    print(f"  SUCCESS: Port {port} is OPEN on {host}")
                    s.close()
                    
                    # Try SMTP login if user/pass are available
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        try:
                            if port == 465:
                                with smtplib.SMTP_SSL(host, port, timeout=5) as server:
                                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                                    print("  SUCCESS: SMTP Login worked!")
                            else:
                                with smtplib.SMTP(host, port, timeout=5) as server:
                                    server.starttls()
                                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                                    print("  SUCCESS: SMTP Login worked!")
                        except Exception as login_e:
                            print(f"  FAILURE: Login failed: {login_e}")
                else:
                    print(f"  FAILURE: Port {port} is CLOSED or Unreachable (Error Code: {result})")
                s.close()
            except Exception as e:
                print(f"  CRITICAL ERROR: {e}")

if __name__ == "__main__":
    diagnostic()
