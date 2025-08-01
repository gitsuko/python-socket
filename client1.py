import socket as so

try:
    print("trying connection to server...")
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)

    address = ("127.0.0.1", 9000)
    conn.connect(address)

    conn.setblocking(True)
    
    print("connected to server.")

    def send_msg(msg):
        conn.send(msg.encode())

        return msg
    
    def recv_msg():
        try:
            conn.settimeout(2.0)
            msg = conn.recv(1024)

            print(f"client 2 said - {msg.decode()}")
            return msg.decode()
        
        except so.timeout:
            print("server timeout, no msg available.")

    print("enter to send or enter 1 to recv.")
    while True:
        user = input()

        if user == '1':
            msg = recv_msg()
        else:
            msg = send_msg(user)

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