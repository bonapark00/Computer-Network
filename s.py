# coding=utf-8
import tkinter as tk
import socket
import threading
import time

window = tk.Tk()
window.title("Bona & Eric's Chat Program")

toppestFrame = tk.Frame(window)
displayFrame = tk.Frame(window)
clientListFrame = tk.Frame(window)


button_startServer = tk.Button(toppestFrame, text="서버 시작", command=lambda : toggleServer())
button_startServer.pack(side=tk.LEFT)
toppestFrame.pack(side=tk.TOP, pady=(5, 0))


label_host = tk.Label(displayFrame, text = "호스트: localhost")
label_host.pack(side=tk.LEFT)
label_port = tk.Label(displayFrame, text = "포트:8080")
label_port.pack(side=tk.LEFT)
displayFrame.pack(side=tk.TOP, pady=(5, 0))


lblLine = tk.Label(clientListFrame, text="현재 접속중인 유저").pack()
scrollBar = tk.Scrollbar(clientListFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
content = tk.Text(clientListFrame, height=15, width=45)
content.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=content.yview)
content.config(yscrollcommand=scrollBar.set, background="#FFFAD4", highlightbackground="grey", state="disabled")
clientListFrame.pack(side=tk.BOTTOM, pady=(3, 12))


server = None
HOST_ADDR = "localhost"
HOST_PORT = 8080
client_name = " "
clients_sockets = []
clients_names = []


def toggleServer():
    button_startServer.config(state=tk.DISABLED)
    button_startServer.config(text="서버 실행중")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)
    threading._start_new_thread(acceptClients, (server, " "))


def acceptClients(accepted, y):
    while True:
        client, addr = accepted.accept()
        clients_sockets.append(client)
        threading._start_new_thread(controlMessage, (client, addr, False))


def controlMessage(client_connection, client_ip_addr, reconnect):
    client_name = client_connection.recv(4096).decode()
    welcome_msg = "Hi \'" + client_name + "\'님!\n + \
                 Welcome to 'Bona & Eric's Chat Program! \
                '/exit'으로 접속 종료 해주세요!"
    client_connection.send(welcome_msg.encode())
    client_name += ": " + str(client_ip_addr)
    clients_names.append(client_name)
    userUpdate(clients_names)

    while True: 
        data = client_connection.recv(4096).decode()

        if not data: 
            idx = getIndex(clients_sockets, client_connection)
            del clients_names[idx]
            del clients_sockets[idx]
            client_connection.send("bye".encode())
            client_connection.close()
            userUpdate(clients_names)
            break

        if data == "/exit":  # einfnormal exit thorugh the box
            idx = getIndex(clients_sockets, client_connection)
            del clients_names[idx]
            del clients_sockets[idx]
            client_connection.close()
            userUpdate(clients_names)
            break

        if str(data) == "FILE":
            idx = getIndex(clients_sockets, client_connection)
            fileName = client_connection.recv(4096).decode()
            lenOfFile = client_connection.recv(4096).decode()
            for c in clients_sockets:
                if c != client_connection:
                    c.send("FILE".encode())
                    time.sleep(0.1)
                    c.send(fileName.encode())
                    time.sleep(0.1)
                    c.send(lenOfFile.encode())
                    time.sleep(0.1)
                    c.send(clients_names[idx].encode())
                    time.sleep(0.1)

            count = 0

            while str(count) != lenOfFile:
                data = client_connection.recv(4096)
                count = count + len(data)
               
                i = 0
                for c in clients_sockets:
                    if c != client_connection:
                        try: 
                            c.send(data)
                            i+=1
                        except:
                            c.close()

        else:
            client_msg = data

            idx = getIndex(clients_sockets, client_connection)
            sending_client_name = clients_names[idx]

            for c in clients_sockets:
                if c != client_connection:
                    server_msg = str(sending_client_name + " -> " + client_msg)
                    c.send(server_msg.encode())

def getIndex(client_list, curr_client):
    if client_list:
        i = 0
        for conn in client_list:
            if conn == curr_client:
                break
            i += 1
        return i
    return False

def userUpdate(name_list):
    content.config(state=tk.NORMAL)
    content.delete('1.0', tk.END)
    for c in name_list:
        content.insert(tk.END, c+"\n")
    content.config(state=tk.DISABLED)


window.mainloop()
