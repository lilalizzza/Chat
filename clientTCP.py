import errno # errores
import socket #sockets
import threading #Hilos
import tkinter # Interfaz
import tkinter.scrolledtext #Desplazamiento
from tkinter import *
#from PIL import Image, ImageTk
from windowLog import * #Llama al windowlog
HEADER_LENGTH = 10
HOST = "172.31.6.16"
PORT = 8000

#172.26.163.80
#127.0.0.1
#192.168.56.1
#79C1F1 Color azul

class Client: 
    
    def __init__(self, host, port,len_header):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.header_length = len_header
        self.users_connected = []
        self.buttons = []
        self.msg_list = None
        self.nickname = windowlogin()
        if not len(self.nickname):
             exit(0)
        username = self.nickname.encode('utf-8')       
        username_header = f"{len(username): < {self.header_length}}".encode('utf-8')
        self.sock.send(username_header + username)
        self.gui_done = False
        self.running = True
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive_messages)
        gui_thread.start()
        receive_thread .start()   
        
    def gui_loop(self):
        self.window = tkinter.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)  # Agrega la opción para cerrar la ventana    
        self.window.title("Cliente TCP")
        self.window.geometry("400x400")
        self.window.configure(bg = "#80D2F6")
        self.canvas = tkinter.Canvas(
            self.window,
            bg = "#2CEFD7",
            height = 0,
            width = 0,
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
        self.msg_list = tkinter.Listbox(self.window, font="Georgia 8 bold", bg="#ffffff", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar.set)
        self.camp_conversation.place(
            x = 500, y = 500,
            width = 500,  #ancho
            height = 500)  #altura
        self.msg_list.place(   #Donde se muestran los mensajes
            x = 22, y = 58,
            width = 245,
            height = 263)
        self.camp_users = tkinter.Frame(self.window)          
        self.scrollbar3 = tkinter.Scrollbar(self.camp_users)
        self.scrollbar4 = tkinter.Scrollbar(self.camp_users)
        self.user_list = tkinter.Listbox(self.window, height=90, width=90, font="Georgia 11 bold", bg="#ffffff", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar3.set)
        self.camp_users.place(
            x = 900, y = 200,
            width = 200,
            height = 200)
        self.user_list.place(
            x = 11, y = 47,
            width = 200,
            height = 260)


        self.label5 = tkinter.Label(self.window, text="CHAT CON TCP",font="Georgia 23 italic bold",bg = "#43A8D5",fg = "#555555")
        self.label5.place(
            x = 80, y = 9)

      
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

       #Boton de enviar
        self.b_send = tkinter.Button(
            self.window,
            highlightbackground = "#32CCFE", 
            highlightcolor= "#32CCFE",
            bg = "#C12828",
            fg = "#ffffff",
            font="Georgia 10 bold",
            text = "ENVIAR",
            borderwidth = 0,
            highlightthickness = 3,
            command = self.send,
            relief = "flat")
        self.b_send.place(
             x = 270, y = 330,
          
            width = 100,
            height = 30)  

         # Crea el botón para cerrar la ventana
        self.b_exit = tkinter.Button(
            self.window,
            highlightbackground = "#32CCFE", 
            highlightcolor= "#32CCFE",
            bg = "#C12828",
            fg = "#ffffff",
            font="Georgia 10 bold",
            text = "X",
            borderwidth = 0,
            highlightthickness = 3,
            command = self.window.destroy,
            relief = "flat")        
        self.b_exit.place(
            x = 370, y = 4,
            width = 20,
            height = 20)


        self.window.resizable(False, False)

        self.gui_done = True

        self.window.protocol("WM_DELETE_WINDOW", self.stop)

        self.window.mainloop()
      # Función para cerrar la ventana
    def close_window(self):
        self.sock.close()  # Cierra la conexión del socket
        self.window.destroy()  # Cierra la ventana       
    def send(self):
        try:
            receiver = self.receiver_data.get()
            message = self.message_data.get()
            self.message_data.set("")

            if not receiver and len(self.user_list.curselection())!=0:
                receiver = self.user_list.get(self.user_list.curselection())

            if not receiver:
                self.msg_list.insert(tkinter.END,"Selecciona un usuario")

            if not message:
                self.msg_list.insert(tkinter.END,"Debe escribir un mensaje a enviar.")

            if receiver == 'all':
                self.receiver_data.set("")
             
            if receiver and message:
                self.msg_list.insert(tkinter.END, self.nickname + "(Tú): " + message )
                receiver = receiver.encode('utf-8')
                message = message.encode('utf-8')
                receiver_header = f"{len(receiver):<{self.header_length}}".encode('utf-8')
                message_header = f"{len(message):<{self.header_length}}".encode('utf-8')
                self.sock.send(receiver_header + receiver + message_header + message)
        except Exception as e:
                print('Error: ', str(e))
                exit()
    def stop(self):
        self.running = False
        self.receiver_data.set("server")
        self.message_data.set("quit")
        self.send()
        self.window.quit()
        exit()
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
        self.user_list = tkinter.Listbox(self.window, height=11, width=38, font="Arial 11 bold", bg="#ffffff", borderwidth = 0,highlightthickness = 0,yscrollcommand=self.scrollbar3.set)
        self.user_list.place(
            x = 270, y = 58,
            width = 100,
            height = 263)

        for user_connected in self.users_connected:
            self.user_list.insert(tkinter.END, user_connected)

    def receive_messages(self):
        while self.running:
            try:
                username_header = self.sock.recv(10)
                if not len(username_header):
                    print("Conexión cerrada con el servidor")
                    self.sock.close()
                    exit()
                username_decode = username_header.decode('utf-8').strip()
                username_length = int(username_decode)
                username = self.sock.recv(username_length).decode('utf-8')
                    
                message_header = self.sock.recv(10)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.sock.recv(message_length).decode('utf-8')
                
                if username == 'server':
                    if message == 'user_connected':
                        user_connected_header = self.sock.recv(10)
                        user_connected_length = int(user_connected_header.decode('utf-8').strip())
                        user_connected = self.sock.recv(user_connected_length).decode('utf-8')
                        self.user_connected(user_connected)
                    elif message == 'user_disconnected':
                        user_disconnected_header = self.sock.recv(10)
                        user_disconnected_length = int(user_disconnected_header.decode('utf-8').strip())
                        user_disconnected = self.sock.recv(user_disconnected_length).decode('utf-8')
                        self.user_disconnected(user_disconnected)
                    else:
                        self.server_message(message)
                else:
                    self.normal_message(username, message)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print ('Leyendo error: ', str(e))
                    return
                continue  

            except Exception as e:
                print('Error general: ', str(e))
                exit

client = Client(HOST, PORT, HEADER_LENGTH)