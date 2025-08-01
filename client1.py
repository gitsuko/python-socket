import socket as so
import threading as th
from queue import Queue

try:
    print("trying connection to server...")
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)

    address = ("127.0.0.1", 9000)
    conn.connect(address)
    conn.settimeout(1.0)

    conn.setblocking(True)
    
    print("connected to server.")

    def send_msg(q):
        msg = input()

        if msg.strip() != "":
            conn.send(msg.encode())
            print(f"message sent successfuly - {msg}")
        else:
            msg == "..."

        q.put(msg)
    
    def recv_msg():
        try:
            msg = conn.recv(1024)
            if msg:
                if msg.decode() != "!":
                    print(f"client 2 said - {msg.decode()}")
            else:
                print("exiting...")
                exit(0)
            
            return msg.decode()
        
        except so.timeout:
            pass

    print("== enter text to send message or 'exit' for exiting ==")
    while True:

        q = Queue()

        send_thread = th.Thread(target=send_msg, args=(q,))
        send_thread.start()

        while send_thread.is_alive():
            
            msg = recv_msg()

            if msg == "exit":
                print("exiting...")
                exit(0)
                break


        send_thread.join()

        msg = q.get()
        

        if msg == "exit":
            break

    try:
        conn.close()
    except: ...

    print("closing connection...")

except Exception as e:

    try:
        conn.close()
    except: ...

    print(f"connection failed - {e}")