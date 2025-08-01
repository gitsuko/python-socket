import socket as so
import threading as th
from queue import Queue

try:
    print("server waiting for connection...")
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)

    address = ("127.0.0.1", 9000)
    conn.bind(address)

    conn.listen(2)
    conn.setblocking(True)

    client1, addr = conn.accept()
    print("client1 connected.")

    client2, addr = conn.accept()
    print("client2 connected.")


    client1.settimeout(1.0)
    client2.settimeout(1.0)

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
                print(f"client 1 - {msg_1}")

            if msg_1 == "exit":
                break

        if  msg_2 != None:
            if msg_2.strip() != "":
                client1.send(msg_2.encode())
                print(f"client 2 - {msg_2}")

            if msg_2 == "exit":
                break
        

    try:
        client1.close()
        client2.close()
        conn.close()
    except:
        pass

    print("connected closed.")
        

except Exception as e:

    try:
        client1.close()
    except: ...
    try:
        client2.close()
    except: ...
    try:
        conn.close()
    except: ...

    print(f"connection failed - {e}")
