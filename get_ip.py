import socket

def get_host_ip():
    try:
        # Use a dummy connection to get the local IP address used for outbound traffic
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Google's DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'  # fallback

if __name__ == "__main__":
    print("Private IP Address:", get_host_ip())
