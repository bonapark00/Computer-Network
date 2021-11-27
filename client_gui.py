from posixpath import basename
import tkinter as tk
from tkinter import messagebox
import socket
import threading
from tkinter import filedialog
import time
import os



window = tk.Tk()
window.title("Client")
username = " "


topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
#btnConnect.bind('<Button-1>', connect)
topFrame.pack(side=tk.TOP) # positioning Name Frame




displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP) # positioning Text Frame




messageFrame = tk.Frame(window)
tkMessage = tk.Text(messageFrame, height=2, width=55) # put message object inside messageFrame
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10)) # ??
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
# event occurs when user pressed the Enter Key
messageFrame.pack(side=tk.BOTTOM)


fileFrame = tk.Frame(window)
labelFile = tk.Label(fileFrame, height = 5)
labelFile.pack(side=tk.LEFT)

labelFileLocation = tk.Label(fileFrame, text = "Choose file to send", relief="groove")
labelFileLocation.pack(side=tk.LEFT)
                            
bottonBrowse = tk.Button(fileFrame, text = "Browse", command = lambda: browseFile())                            
bottonBrowse.pack(side=tk.LEFT)


bottonSendFile = tk.Button(fileFrame, text = "Send", command = lambda: sendFile())
bottonSendFile.pack(side=tk.LEFT)


fileFrame.pack(side = tk.BOTTOM) # !!


def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = entName.get()
        connect_to_server(username)


# network client
client = None
HOST_ADDR = "localhost"
HOST_PORT = 8080

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Send name to server after connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):

    # keep receiving the socket until the disconnection
    while True:
        from_server = sck.recv(4096).decode() # 0

        if not from_server: break

        if str(from_server) == "FILE":
            fileName = sck.recv(4096).decode() # 1
            print(fileName+"\n")
            lenOfFile = sck.recv(4096).decode()
            print(lenOfFile + "\n")
            sentUser = sck.recv(4096).decode() # 3 
            print(sentUser + " sends to "+ username)

            if os.path.exists(fileName):
                os.remove(fileName)
            total = 0
            fileName = fileName[:-4]
            with open(fileName+"__"+"from_"+sentUser+"_to_"+username+".txt", 'wb') as newFile:
                while str(total) != lenOfFile:
                    data = sck.recv(4096)
                    total += len(data)
                    newFile.write(data)

            tkDisplay.config(state = tk.DISABLED)
            tkDisplay.config(state=tk.NORMAL)
            tkDisplay.insert(tk.END, "\n\nFile named <"+fileName +"> is well received from \""+ sentUser +"\"!\n")
            tkDisplay.config(state = tk.DISABLED)
            tkDisplay.see(tk.END)

        else:

            # display message from server on the chat window
            # enable the display area and insert the text and then disable.
            # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
            texts = tkDisplay.get("1.0", tk.END).strip()
            tkDisplay.config(state=tk.NORMAL)
            if len(texts) < 1:
                tkDisplay.insert(tk.END, from_server)
            else:
                tkDisplay.insert(tk.END, "\n\n"+ from_server)

            tkDisplay.config(state=tk.DISABLED)
            tkDisplay.see(tk.END)


    sck.close()
    print(username + "'s socket closed")
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END) # clear the sent msg


def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")


def browseFile():
    global fileName
    fileName = filedialog.askopenfilename(initialdir="/", 
                                    title="Select a file",
                                    filetypes = (("Text files", 
                                                "*.txt*"), 
                                                ("all files", 
                                                "*.*")))
    labelFileLocation.configure(text="File Opened: "+ fileName)


def sendFile():
    global client # needed?!

    client.send("FILE".encode())    # telling to the server that 
                                    # the client is now send a file! not msg
    time.sleep(0.1)
    print("okay 1")
    client.send(os.path.basename(fileName).encode())
    time.sleep(0.1)
    print("okay 2")

    client.send(str(os.path.getsize(fileName)).encode())
    time.sleep(0.1)
    print("okay 3")

    file = open(fileName, "rb")
    data = file.read(4096)

    while data:
        client.send(data)
        data = file.read(4096)
    
    tkDisplay.config(state=tk.DISABLED)
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.insert(tk.END, "\n\nYour File-> "+ fileName)
    tkDisplay.config(state=tk.DISABLED)
    tkDisplay.see(tk.END)

    print("\n File well sent from " + username + "\n\n")


window.mainloop()
