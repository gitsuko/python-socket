from datetime import datetime as dt
import threading as th
from time import sleep
import logging as lo
import socket as so
import sys
try:
    import tkinter as tk
except ModuleNotFoundError:
    print("tkinter is not installed. Try this command:")
    print("sudo apt install python3-tk")
    sys.exit("exiting...")

# ============== LOGGING SETUP ==============
format = "%(asctime)s - %(message)s"
lo.basicConfig(format=format, level=lo.INFO, datefmt="%H:%M:%S")

# ============== MAIN CODE ==============
IP_ADDRESS = input("Enter IP address to connect: ")
try:
    def recv_message():
        """
        Receive a message from server.
        It will ignore the message if it's the broadcast (msg = !)
        """
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                if data != "!":

                    data_info = data.split("-")[0]
                    if str(client_port) == data_info.split(":")[1].strip():
                        data = data.split(":")[2]
                        text_box.tag_configure(tk.RIGHT, justify=tk.RIGHT)
                        text_box.config(state=tk.NORMAL)
                        text_box.insert(tk.END, f"{data}\n", tk.RIGHT)
                        text_box.config(state=tk.DISABLED)
                        text_box.see(tk.END)
                    else:
                        text_box.config(state=tk.NORMAL)
                        text_box.insert(tk.END, f"{data}\n")
                        text_box.config(state=tk.DISABLED)
                        text_box.see(tk.END)
            except so.timeout:
                continue
            except Exception as e:
                print(f"[Receive Error] {e}")
                break

    def send_message():
        """
        Sends a message to server only If message is not empty string
        """
        msg = entry.get()
        if msg.strip() == "":
            return
        try:
            conn.send(msg.encode())
            entry.delete(0, tk.END)
        except Exception as e:
            print(f"[Send Error] {e}")    
    
    def on_closing():
        """
        Close both the connection and GUI window properly
        """
        try:
            # define a long text for server exiting,
            # so user have less chance of using it
            conn.send("client_exit_server".encode())
            sleep(0.8) # to avoid Broken pipe error from server
            conn.close()
        except:
            pass
        window.destroy()

    def get_uptime():
        """
        Calculate and prints the clinet up time on window
        """
        while True:
            time_stop = dt.now()
            total = time_stop - time_start

            total_seconds = int(total.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}" # No milliseconds printed

            client_upTime.config(text=f"Up time: {formatted_time}")
            sleep(1) # update every second
    
    time_start = dt.now()
    
    # ============== SOCKET SETUP ==============
    conn = so.socket(so.AF_INET, so.SOCK_STREAM)
    address = (IP_ADDRESS, 9000)
    conn.connect(address)
    conn.settimeout(1.0)
    conn.setblocking(True)

    addr, port = conn.getpeername()
    client_port = conn.getsockname()[1]

    # ============== GUI SETUP ==============
    window = tk.Tk()
    window.title(f"Room info: {addr}:{port}")
    window.config(bg="skyblue")

    text_box = tk.Text(window, width=60, height=20, font=20)
    text_box.config(state=tk.DISABLED)
    text_box.pack(padx=10, pady=10)

    entry = tk.Entry(window, width=60)
    entry.pack()
    # Bind the Return keyword to submit
    entry.bind("<Return>", lambda event: send_message())

    lower_frame = tk.Frame(window, bg="skyblue")
    lower_frame.pack(pady=15)

    send_button = tk.Button(lower_frame, text="Send", command=send_message)
    send_button.config(fg="white", bg="grey")
    send_button.pack(pady=(0, 10), side=tk.RIGHT)

    client_upTime = tk.Label(lower_frame, text="Up time: ", bg="skyblue")
    client_upTime.pack(side=tk.RIGHT, padx=(0, 70))

    window.protocol("WM_DELETE_WINDOW", on_closing)

    # ============== THREADING SETUP ==============
    recv_thread = th.Thread(target=recv_message, daemon=True)
    uptime_thread = th.Thread(target=get_uptime, daemon=True)
    recv_thread.start()
    uptime_thread.start()

    window.mainloop()

except Exception as e:

    try:
        sleep(0.3)
        conn.close()
    except Exception as e:
        lo.warning(f"Failed to close server: {e}")

    lo.error(f"Connection failed - {e}")