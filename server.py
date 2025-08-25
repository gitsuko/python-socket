import socket
import threading
import logging
from get_ip import get_host_ip

format = "%(asctime)s - %(levelname)s - %(message)s"

root = logging.getLogger()
root.setLevel(logging.INFO)

fileHandler = logging.FileHandler("server_logs.txt")
fileHandler.setFormatter(logging.Formatter(format, datefmt="%H:%M:%S"))

consoleHanlder = logging.StreamHandler()
consoleHanlder.setFormatter(logging.Formatter(format, datefmt="%H:%M:%S"))

root.addHandler(fileHandler)
root.addHandler(consoleHanlder)

try: # creating a connection for clients
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """
    Allow the server to reuse the same address after the program exits.
    This prevents the "Address already in use" error caused by the OS holding
    the socket in TIME_WAIT state after a recent close."""
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    IP_ADDRESS = get_host_ip()
    address = (IP_ADDRESS, 9000)
    root.info(f"Server started on {IP_ADDRESS}:{9000}.")

    conn.bind(address)

    conn.listen(2)
    conn.setblocking(True)
    conn.settimeout(1.0)

    clients_database = {} # define a database for clients
    next_id = 1

    def add_client_database(client_socket: socket.socket ,address: str, port: int):
        """
        Adds a new connected client with address and port to the database.

        Args:
            client_socket (socket.socket): client's socekt information for later send or recieve data
            address (str): client's IP address
            port (int): clients's port
        """
        global next_id

        clients_database[str(next_id)] = {
            "socket": client_socket,    
            "address": f"{address}",
            "port": f"{port}"
        }

        next_id += 1

    def accept_connection():
        """
        This function waits for incoming connections and if new connection accepted,
        calls add_client_database().
        """
        try:    
            client, addr = conn.accept()
            client.settimeout(1.0)
            client_addr, client_port = addr

            root.info(f"New client connected from {client_addr}:{client_port}")

            database_thread = threading.Thread(target=add_client_database, args=(client, client_addr, client_port))
            database_thread.start()
            database_thread.join()

        except socket.timeout:
            pass # in case no one joined the server
        except Exception as e:
            root.error(f"Error occured while accepting a connection: {e}")

    def client_receive():
        """
        receive messages from clients.

        if no message received, it will move on.
        """
        try:
            target_id = "" # in case user sent "exit" to removing from database

            for client_id, client_info in list(clients_database.items()):
                client_socket = client_info["socket"]
                client_addr = client_info["address"] +":"+ str(client_info["port"])
                try:
                    data = client_socket.recv(1024)
                    if data.strip() != "":
                        if data != None:    

                            if data.decode() == "client_exit_server":
                                target_id = client_id
                                target_addr = client_addr
                                content = client_addr + " - sent: " + data.decode()
                                root.info(content)
                            else:
                                content = client_addr + " - sent: " + data.decode()
                                root.info(content)

                                client_send(msg=content)

                    else:
                        pass # if received data is None
                except socket.timeout:
                    pass
                except Exception as e:
                    root.error(f"Error occured in client_receive function: {e}")
            
            if target_id.strip() != "":

                client_exit_thread = threading.Thread(target=client_exit, args=(target_id,))
                client_exit_thread.start()
                client_exit_thread.join()

                client_send(msg=f"{target_addr} exited the server.")
        
        except RuntimeError:
            root.error("RuntimeError occured in client receive function.")

    def client_send(msg: str):
        """
        Sends the recieved message to all existing  clients

        Args:
            msg (str): This content includes client address and client message
        """
        for client_id, client_info in list(clients_database.items()):
            client_socket = client_info["socket"]
            client_addr = client_info["address"] +":"+ str(client_info["port"])
            
            try:
                client_socket.send(msg.encode())
            except Exception as e:
                root.error(f"error in slient_send function: {e}")

    def broadcast():
        """
        Sends a broadcast message to all clients to maintain active connections.
        """
        for client_id, client_info in list(clients_database.items()):
            client_socket = client_info["socket"]

            client_socket.send("!".encode())

    def client_exit(target_id):
        """
        delete a client from database

        Args:
            target_id: Which is client's ID saved in database
        """
        client_info = clients_database.get(target_id)
        if client_info:
            try:
                client_info["socket"].close()
            except Exception as e:
                root.warning(f"Failed to close client socket: {e}")
            del clients_database[target_id]


    # ================ Main Code ================
    root.info("Waiting for messages... (Ctrl+C to close the connection)")

    while True:
        
        if len(clients_database) > 0: # if client exist
            thread = threading.Thread(target=client_receive)
            thread.start()

            while thread.is_alive(): # if there are no incoming massages, check for new connections
                accept_connection()
                broadcast()

            thread.join()
        else:
            accept_connection()


except KeyboardInterrupt:
    root.info("Ctrl+C pressed")

    try:
        for client_id, client_info in list(clients_database.items()):
            client_socket = client_info["socket"]
            client_socket.close()
    except Exception as  e:
        root.warning(f"Failed to close client: {e}")
    try:
        conn.close()
    except Exception as e: 
        root.warning(f"Failed to close server: {e}")

    root.info("Connection closed.")

except Exception as e:

    try:
        for client_id, client_info in list(clients_database.items()):
            client_socket = client_info["socket"]
            client_socket.close()
    except Exception as  e:
        root.warning(f"Failed to close client: {e}")
    try:
        conn.close()
    except Exception as e: 
        root.warning(f"Failed to close server: {e}")

    root.error(f"Connection failed: {e}")