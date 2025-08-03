import socket as so
import threading as th
from queue import Queue
import logging as lo

format = "%(asctime)s - %(levelname)s - %(message)s"
lo.basicConfig(format=format, level=lo.INFO, datefmt="%H:%M:%S")

IP_ADDRESS = input("Enter IP address to connect: ")

try:
    lo.info("Trying connection to server...")
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)

    address = (IP_ADDRESS, 9000)
    conn.connect(address)
    conn.settimeout(1.0)

    conn.setblocking(True)
    
    addr = conn.getpeername()[0]
    port = conn.getpeername()[1]

    lo.info(f"Connected to server {addr}:{port}")

    def send_msg(q):
        msg = input()

        if msg.strip() != "":
            conn.send(msg.encode())
            lo.info(f"You sent: {msg}")
        else:
            msg == "..."

        q.put(msg)
    
    def recv_msg():
        try:
            msg = conn.recv(1024)
            if msg:
                if msg.decode() != "!":
                    lo.info(f"Client #2 sent: {msg.decode()}")
            else:
                lo.info("Exiting...")
                exit(1)
            
            return msg.decode()
        
        except so.timeout:
            pass

    print("NOTE: \"enter text to send message or 'exit' for exiting\"")
    while True:

        q = Queue()

        send_thread = th.Thread(target=send_msg, args=(q,))
        send_thread.start()

        while send_thread.is_alive():
            
            msg = recv_msg()

            if msg == "exit":
                print("Enter a key to exit.")
                exit(0)

        send_thread.join()

        msg = q.get()

        if msg == "exit":
            break

    try:
        conn.close()
    except Exception as e:
        lo.warning(f"Failed to close server: {e}")

    lo.info("closing connection")

except Exception as e:

    try:
        conn.close()
    except Exception as e:
        lo.warning(f"Failed to close server: {e}")

    lo.error(f"Connection failed - {e}")