import socket as so
import threading as th
from queue import Queue
import logging as lo

format = "%(asctime)s - %(levelname)s - %(message)s"
lo.basicConfig(format=format, level=lo.INFO, datefmt="%H:%M:%S")

try: # creating a connection for clients with timeout
    lo.info("Server started. Waiting for connections...")
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)

    # Allow the server to reuse the same address after the program exits.
    # This prevents the "Address already in use" error caused by the OS holding
    # the socket in TIME_WAIT state after a recent close.
    conn.setsockopt(so.SOL_SOCKET, so.SO_REUSEADDR, 1)

    address = ("127.0.0.1", 9000)
    conn.bind(address)

    conn.listen(2)
    conn.setblocking(True)

    client1, addr = conn.accept()
    client1_addr = client1.getpeername()[0]
    client1_port = client1.getpeername()[1]
    
    lo.info(f"Client #1 connected from {client1_addr}:{client1_port}")

    client2, addr = conn.accept()
    client2_addr = client2.getpeername()[0]
    client2_port = client2.getpeername()[1]

    lo.info(f"Client #2 connected from {client2_addr}:{client2_port}")

    client1.settimeout(1.0)
    client2.settimeout(1.0)

    # message receive functions for adding to threads
    def client1_recv(q1):
        try:
            data_1 = client1.recv(1024)
        
            q1.put(data_1.decode())
        
        except so.timeout:
            q1.put("")
    
    def client2_recv(q2):
        try:
            data_2 = client2.recv(1024)
        
            q2.put(data_2.decode())
        
        except so.timeout:
            q2.put("")

    # Main Code
    lo.info("Waiting for messages...")
    
    while True:

        q1 = Queue()
        q2 = Queue()

        thread_1 = th.Thread(target=client1_recv, args=(q1, ))
        thread_2 = th.Thread(target=client2_recv, args=(q2, ))

        thread_1.start()
        thread_2.start()

        thread_1.join()
        thread_2.join()

        # getting messages from queue
        msg_1 = q1.get()
        msg_2 = q2.get()

        if msg_1 != None:
            if msg_1.strip() != "":
                client2.send(msg_1.encode())
                lo.info(f"Client #1 sent: {msg_1}")
                    
            if msg_1 == "exit":
                break

        if  msg_2 != None:
            if msg_2.strip() != "":
                client1.send(msg_2.encode())
                lo.info(f"Client #2 sent: {msg_2}")
            
            if msg_2 == "exit":
                break
        
        # sending clients a message as a broadcast
        # to help them receive messages in their scripts
        client1.send("!".encode())
        client2.send("!".encode())

    try:
        client1.close()
    except Exception as e:
        lo.warning(f"Failed to close client #1: {e}")
    try:
        client2.close()
    except Exception as e:
        lo.warning(f"Failed to close client #2: {e}")
    try:
        conn.close()
    except Exception as e: 
        lo.warning(f"Failed to close server: {e}")
    
    lo.info("Connection closed.")


except Exception as e:

    try:
        client1.close()
    except Exception as e:
        lo.warning(f"Failed to close client #1: {e}")
    try:
        client2.close()
    except Exception as e:
        lo.warning(f"Failed to close client #2: {e}")
    try:
        conn.close()
    except Exception as e: 
        lo.warning(f"Failed to close server: {e}")

    lo.error(f"Connection failed: {e}")