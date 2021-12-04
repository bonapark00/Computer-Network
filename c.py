# coding=utf-8
import tkinter as tk
from tkinter import messagebox
import socket
import threading
from tkinter import filedialog
import time
import os

window = tk.Tk()
window.title("클라이언트")
username = " "

toppestFrame = tk.Frame(window)
diplayFrame = tk.Frame(window)
contentFrame = tk.Frame(window)
fileFrame = tk.Frame(window)


LabelLine = tk.Label(toppestFrame).pack()
labelName = tk.Label(toppestFrame, text="유저:").pack(side=tk.LEFT)
EntryName = tk.Entry(toppestFrame)
EntryName.pack(side=tk.LEFT)
Connect = tk.Button(toppestFrame, text="서버 접속", command=lambda: joinChat())
Connect.pack(side=tk.LEFT)
toppestFrame.pack(side=tk.TOP)

Line = tk.Label(diplayFrame).pack()
textBox = tk.Text(diplayFrame, height=40, width=70)
textBox.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
textBox.tag_config("tag_your_message", foreground="blue")
textBox.config(background="#FFFAD4", highlightbackground="grey", state="disabled")
diplayFrame.pack(side=tk.TOP)

Content = tk.Text(contentFrame, height=5, width=70)
Content.pack(side=tk.LEFT, padx=(4, 13), pady=(3, 10))
Content.config(highlightbackground="black", state="disabled")
Content.bind("<Return>", (lambda event: getChat(Content.get("1.0", tk.END))))
contentFrame.pack(side=tk.BOTTOM)

labelFile = tk.Label(fileFrame, height=5)
labelFile.pack(side=tk.LEFT)
labelFileLocation = tk.Label(fileFrame, text="파일을 선택해주세요", relief="groove")
labelFileLocation.pack(side=tk.LEFT)
Browse = tk.Button(fileFrame, text="파일 선택", command=lambda: browseFile())
Browse.pack(side=tk.LEFT)
SendFile = tk.Button(fileFrame, text="전송", command=lambda: sendFile())
SendFile.pack(side=tk.LEFT)
fileFrame.pack(side=tk.BOTTOM)

client = None
HOST_ADDR = "localhost"
HOST_PORT = 8080

def joinChat():
    global username, client
    if len(EntryName.get()) < 1:
        tk.messagebox.showerror(title="에러 발생", message="입력이 없습니다. 다시 입력해주세요.")
    else:
        username = EntryName.get()
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST_ADDR, HOST_PORT))
            client.send(username.encode())

            EntryName.config(state=tk.DISABLED)
            Connect.config(state=tk.DISABLED)
            Content.config(state=tk.NORMAL)

            threading._start_new_thread(receiveMessage, (client, "m"))
        except Exception:
            tk.messagebox.showerror(title="에러 발생", message=HOST_ADDR + " 호스트 " + str(HOST_PORT) + " 포트에 연결 불가.")


def receiveMessage(sckt, m):

    while True:
        from_server = sckt.recv(4096).decode()
        if not from_server:
            break

        if str(from_server) == "FILE":
            fileName = sckt.recv(4096).decode()
            print(fileName + "\n")
            lenOfFile = sckt.recv(4096).decode()
            print(lenOfFile + "\n")
            sentUser = sckt.recv(4096).decode()
            print(sentUser + " -> " + username)

            i=0
            for c in sentUser:
                if c==":":
                    sentUser=sentUser[:i]
                    break
                else:
                    i+=1
        
            total = 0
            fileName = fileName[:-4]
            with open(fileName +"_from_"+sentUser +"_to_" + username + ".txt", 'wb') as newFile:
                while str(total) != lenOfFile:
                    data = sckt.recv(4096)
                    total += len(data)
                    newFile.write(data)

            textBox.config(state=tk.DISABLED)
            textBox.config(state=tk.NORMAL)
            textBox.insert(tk.END, "\n\n<" + fileName + "> 파일을 \"" + sentUser + "\"로부터 받았습니다!\n")
            textBox.config(state=tk.DISABLED)
            textBox.see(tk.END)
 

        else:
            texts = textBox.get("1.0", tk.END).strip()
            textBox.config(state=tk.NORMAL)

            if len(texts) < 1:
                textBox.insert(tk.END, from_server)
            else:
                textBox.insert(tk.END, "\n\n" + from_server)

            textBox.config(state=tk.DISABLED)
            textBox.see(tk.END)

    sckt.close()
    window.destroy()



def getChat(msg):
    msg = msg.replace('\n', '')
    texts = textBox.get("1.0", tk.END).strip()
    textBox.config(state=tk.NORMAL)
    if len(texts) > 0:
        textBox.insert(tk.END, "\n\n" + "나 -> " + msg, "tag_your_message")

    textBox.config(state=tk.DISABLED)
    sendChat(msg)
    textBox.see(tk.END)
    Content.delete('1.0', tk.END)


def sendChat(msg):
    client_msg = str(msg)
    if len(client_msg) == 0:
        tk.messagebox.showerror(title="에러 발생", message="입력이 없습니다. 다시 입력해주세요.")
    elif client_msg == "/exit":
        client.send(client_msg.encode())
        client.close()
        window.destroy()
    else:
        client.send(client_msg.encode())


def browseFile():
    global fileName
    fileName = filedialog.askopenfilename(initialdir="/",
                                          title="Choose a file",
                                          filetypes=(("txt",
                                                      "*.txt*"),
                                                     ("others",
                                                      "*.*")))
    labelFileLocation.configure(text="Chosen file: " + fileName)


def sendFile():
    global client

    client.send("FILE".encode())
    time.sleep(0.1)
    client.send(os.path.basename(fileName).encode())
    time.sleep(0.1)
    client.send(str(os.path.getsize(fileName)).encode())
    time.sleep(0.1)

    file = open(fileName, "rb")
    data = file.read(4096)

    while data:
        client.send(data)
        data = file.read(4096)
      

    textBox.config(state=tk.DISABLED)
    textBox.config(state=tk.NORMAL)
    textBox.insert(tk.END, "\n\n보낸 파일-> " + fileName)
    textBox.config(state=tk.DISABLED)
    textBox.see(tk.END)


def abnormal_closing(): 
    if client:
        client.send("비정상적인 종료".encode())
        if not messagebox.askokcancel("Quit", "비정상적인 종료가 감지 되었습니다. 종료하시겠습니까?"):
            client.send("재접속 성공".encode())
        else:
            client.send("종료되었습니다".encode())
            client.send("/exit".encode())
            window.destroy()

    else:
        window.destroy()


window.protocol("WM_DELETE_WINDOW", abnormal_closing)

window.mainloop()