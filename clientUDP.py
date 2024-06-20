import errno
import socket
import threading
import tkinter
import tkinter.scrolledtext
from windowLog import *
HOST = "172.31.6.16"
#127.0.0.1
#192.168.56.1
PORT = 8000

class Client:     
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.USER_CONNECTED = 'user_connected'
        self.USER_DISCONNECTED = 'user_disconnected'
        self.USER_MESSAGE ='user_message'
        self.ALL_MESSAGE = 'all_message'
        self.BUFFER_SIZE = 4096
        self.users_connected = []
        self.msg_list = None
        self.HOST = host
        self.PORT = port

        self.nickname = windowlogin()
        if not len(self.nickname):
             exit(0)
        
        self.type_of_message = self.USER_CONNECTED
        self.receiver = self.nickname
        self.message = "El usuario " +self.receiver + " se unio al chat!"
        self.information = self.type_of_message+"@"+self.receiver+"@"+self.message
        self.information = self.information.encode('utf-8')
        self.sock.sendto(self.information,(self.HOST,self.PORT))
        
        self.gui_done = False
        self.running = True
        
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive_messages)

        gui_thread.start()
        receive_thread .start()
    
    def gui_loop(self):
        self.window = tkinter.Tk()
            
        self.window.title("Cliente UDP")

        self.window.geometry("400x400")
        self.window.configure(bg = "#2FF55C")
        self.canvas = tkinter.Canvas(
            self.window,
            bg = "#2FF55C",
            height = 525,
            width = 197,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge")
        self.canvas.place(x = 0, y = 0)
        self.sender_data = tkinter.StringVar(self.window)  
        self.receiver_data = tkinter.StringVar(self.window)   
        self.message_data = tkinter.StringVar(self.window)  
        self.camp_conversation = tkinter.Frame(self.window)
        self.scrollbar = tkinter.Scrollbar(self.camp_conversation)
        self.scrollbar2 = tkinter.Scrollbar(self.camp_conversation)
        self.msg_list = tkinter.Listbox(self.window, font="Georgia 8 bold", bg="#dddddd", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar.set)
        self.camp_conversation.place(
            x = 500, y = 500,
            width = 500,
            height = 500)
        self.msg_list.place(
            x = 22, y = 58,
            width = 245,
            height = 263)
        self.camp_users = tkinter.Frame(self.window)
        self.scrollbar3 = tkinter.Scrollbar(self.camp_users)
        self.scrollbar4 = tkinter.Scrollbar(self.camp_users)
        self.user_list = tkinter.Listbox(self.window, height=11, width=38, font="Georgia 11 bold", bg="#dddddd", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar3.set)
        self.camp_users.place(
            x = 900, y = 200,
            width = 200,
            height = 200)
        self.user_list.place(
            x = 11, y = 47,
            width = 200,
            height = 260)
        self.label5 = tkinter.Label(self.window, text="CHAT CON UDP",font="Georgia 23 italic bold",bg = "#2BD051",fg = "#555555")
        self.label5.place(
           x = 80, y = 9
            )
        self.e_message = tkinter.Entry(
            self.window,
            textvariable=self.message_data,
            highlightbackground = "#000000", 
            highlightcolor= "#000000",
            bd = 0,
            bg = "#ffffff",
            highlightthickness = 2)
        self.e_message.place(
            x = 22, y = 330,
            width = 245,
            height = 37)     
        self.b_send = tkinter.Button(
            self.window,
            highlightbackground = "#32CCFE", 
            highlightcolor= "#32CCFE",
            bg = "#C12828",
            fg = "#ffffff",
            font="Arial 10 bold",
            text = "ENVIAR",
            borderwidth = 0,
            highlightthickness = 3,
            command = self.send,
            relief = "flat")
        self.b_send.place(
            x = 270, y = 330,         
            width = 100,
            height = 30)
        self.window.resizable(False, False)
        self.gui_done = True
        self.window.protocol("WM_DELETE_WINDOW", self.stop)
        self.window.mainloop()    
    def send(self):
        try:
            receiver = self.receiver_data.get()
            message = self.message_data.get()
            self.message_data.set("")

            if not receiver and len(self.user_list.curselection())!=0:
                receiver = self.user_list.get(self.user_list.curselection())

            if not receiver:
                self.msg_list.insert(tkinter.END,"Selecciona un nombre de usuario para enviar el mensaje.")

            if not message:
                self.msg_list.insert(tkinter.END,"Escriba un mensaje a enviar.")

            if receiver == 'all':
                self.type_of_message = self.ALL_MESSAGE
                receiver = self.nickname
                self.receiver_data.set("")
            else:
                self.type_of_message = self.USER_MESSAGE
            
            if receiver and message:
                self.msg_list.insert(tkinter.END, self.nickname + "(Tú): " + message )
                self.receiver = receiver
                self.message = message
                self.information = self.type_of_message+"@"+self.receiver+"@"+self.message
                self.information = self.information.encode('utf-8')
                self.sock.sendto(self.information,(self.HOST,self.PORT))


        except Exception as e:
                print('Error: ', str(e))
                exit()


    def send_All(self):
        self.receiver_data.set("all")
        self.send()
    
    def stop(self):
        self.running = False
        self.type_of_message = self.USER_DISCONNECTED
        self.receiver = self.nickname
        self.message = "El usuario " + self.nickname + " salió del chat."
        self.information = self.type_of_message+"@"+self.receiver+"@"+self.message
        self.information = self.information.encode('utf-8')
        self.sock.sendto(self.information,(self.HOST,self.PORT))
        self.sock.close()
        self.window.quit()
        exit(0)
    def server_message(self, message):
        self.msg_list.insert(tkinter.END, message)
    def normal_message(self, username, message):
        self.msg_list.insert(tkinter.END, username + ": " + message )
    def user_connected(self, user_connected):
        self.users_connected.append(user_connected)
        self.create_list()
    def user_disconnected(self, user_disconnected):
        self.users_connected.remove(user_disconnected)       
        self.msg_list.insert(tkinter.END,"El usuario " + user_disconnected + " salió del chat." )
        self.create_list()   
    def create_list(self):
        self.user_list.destroy()
        self.scrollbar3.destroy()
        self.scrollbar4.destroy()
        self.scrollbar3 = tkinter.Scrollbar(self.camp_users)
        self.scrollbar4 = tkinter.Scrollbar(self.camp_users)
        self.user_list = tkinter.Listbox(self.window, height=11, width=38, font="Arial 11 bold", bg="#dddddd", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar3.set)
        self.user_list.place(
            x = 270, y = 58,
            width = 100,
            height = 263)
        for user_connected in self.users_connected:
            self.user_list.insert(tkinter.END, user_connected)
    def decode_message(self,data):
        message = data[2]
        if len(data)>3:
            for index in range(3,len(data)):
                message = message + "@" + data[index]
        return message
    def receive_messages(self):
        while self.running:
            try:
                data, address = self.sock.recvfrom(self.BUFFER_SIZE)
                if not len(data):
                    print("Conexión cerrada con el servidor")
                    self.sock.close()
                    exit()
                data = str(data.decode('utf-8')).split('@')
                if data[0] == self.USER_CONNECTED:
                    if data[2] == 'connected':
                        self.user_connected(data[1])
                    else:
                        self.server_message(data[2])
                elif data[0] == self.USER_DISCONNECTED:
                    self.user_disconnected(data[1])
                else:
                    message = self.decode_message(data)
                    self.normal_message(data[1], message)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    # print ('Leyendo error: ', str(e))
                    return
                continue  
            except Exception as e:
                print('Error general: ', str(e))
                exit

client = Client(HOST, PORT)