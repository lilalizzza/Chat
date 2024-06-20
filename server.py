import socket
import select
import time
import threading

HEADER_LENGTH = 10
IP = "172.31.6.16" 
PORT = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

clients = {}

def UDP_loop():
    USER_CONNECTED = 'user_connected'
    USER_DISCONNECTED = 'user_disconnected'
    USER_MESSAGE ='user_message'
    ALL_MESSAGE = 'all_message'
    BUFFER_SIZE = 4096
    IP = "172.31.6.16" 
    PORT = 8000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((IP, PORT))

    clients = {}

    def encode_messageUDP(data):
        message = data[0]
        for index in range(1,len(data)):
            message = message + "@" + data[index]
        message = message.encode('utf-8')
        return message


    while True:
        try:
            data, address = server_socket.recvfrom(BUFFER_SIZE)
                
            if not len(data):
                nickname = clients[address]
                information ="El usuario "+ nickname + " se ha desconectado."
                print("UDP: ",information)
                message = USER_DISCONNECTED+"@"+nickname+"@"+information
                for client in clients:
                    if client != address:
                        server_socket.sendto(message, client)
                del clients[address]
                
            data = str(data.decode('utf-8')).split('@')

        except Exception as e:
            print('UDP Error: ', str(e))
            continue      
    
        if data[0] == USER_CONNECTED:
            clients[address] = data[1]
            
            print("UDP: ",data[2])

            time.sleep(1) 

            message = encode_messageUDP(data)

            #Envía mensaje de usuario unido al chat
            for client in clients:
                if client != address:
                    server_socket.sendto(message, client)

            #Enviando mensaje de confirmacion de conexion a el usuario   
            data[2]= "Hola "+ data[1] + " ahora puedes chatear."
            message = encode_messageUDP(data)
            server_socket.sendto(message, address)
            
            #Envía usuarios conectados
            data[2]= "connected"
            for client in clients:
                if client != address:
                    data[1] = clients[address]
                    message = encode_messageUDP(data)
                    server_socket.sendto(message, client)
            
                data[1] = clients[client]
                message = encode_messageUDP(data)
                server_socket.sendto(message, address)

            
        elif data[0] == USER_DISCONNECTED:

            message = encode_messageUDP(data)
            
            for client in clients:
                if client != address:
                    server_socket.sendto(message, client)

            del clients[address]
            print("UDP: ",data[2])

        elif data[0] == ALL_MESSAGE:

            print("UDP: ","Recibiste un mensaje de ", data[1])
            
            message = encode_messageUDP(data)
            
            for client in clients:
                if client != address:
                    server_socket.sendto(message, client)
        
        elif data[0] == USER_MESSAGE:

            print("UDP: ","Recibiste un mensaje de ", clients[address])

            receiver = data[1]

            for client in clients:
                nickname = clients[client]
                if nickname  == receiver:
                    data[1] = clients[address]
                    message = encode_messageUDP(data)
                    server_socket.sendto(message, client)


def receive_userTCP(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        
        if not len(message_header):
            return False
        
        message_length = int(message_header.decode('utf-8').strip())
        return{"header": message_header,"data": client_socket.recv(message_length)}
        
    except:
            return False 


def receive_messageTCP(client_socket):
    try:
        receiver_header = client_socket.recv(HEADER_LENGTH)
        
        if not len(receiver_header):
            return False
        
        receiver_length = int(receiver_header.decode('utf-8').strip())
        receiver_data = client_socket.recv(receiver_length)

        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8').strip())
        message_data = client_socket.recv(message_length)
        return{"r_header":receiver_header,"r_data": receiver_data,"m_header": message_header,"m_data": message_data}
    except:
            return False 


UDP_thread = threading.Thread(target=UDP_loop)
UDP_thread.start()

print ("SERVIDOR LISTO")


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_userTCP(client_socket)
            if user is False:
                continue 
            sockets_list.append(client_socket)

            clients[client_socket] = user

            print("TCP: ","NUEVA CONEXIÓN", client_address[0],"PUERTO",client_address[1], "USUARIO: ", user['data'].decode('utf-8'))
            time.sleep(1) 

            #Enviando mensaje de confirmacion de conexion a el usuario
            receiver = "server"
            username = user['data'].decode('utf-8')
            message = "Hola "+ username + " estas conectado"
            receiver = receiver.encode('utf-8')
            message = message.encode('utf-8')
            receiver_header = f"{len(receiver):<{HEADER_LENGTH}}".encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(receiver_header + receiver + message_header + message)

            #Enviando mensaje de reciente conexion de usuario a los demas usuarios que ya estan conectados
            message ="¡"+ username + " se unio al chat!"
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

            message_connect ="user_connected"
            message_connect = message_connect.encode('utf-8')
            message_connect_header = f"{len(message_connect):<{HEADER_LENGTH}}".encode('utf-8')

            for clients_socket in clients:
                if clients_socket != client_socket:
                    clients_socket.send(receiver_header + receiver + message_header + message)
                    clients_socket.send(receiver_header + receiver + message_connect_header + message_connect + user['header'] + user['data'] )
                user_connected = clients[clients_socket]
                client_socket.send(receiver_header + receiver + message_connect_header + message_connect + user_connected['header'] + user_connected['data'])

        else:
            message = receive_messageTCP(notified_socket)
    
            if message is False:
                print(f"Cerrando conexion TCP de {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                user_disconnected = clients[notified_socket]
                message_connect ="user_disconnected"
                message_connect = message_connect.encode('utf-8')
                message_connect_header = f"{len(message_connect):<{HEADER_LENGTH}}".encode('utf-8')
                for clients_socket in clients:
                    if clients_socket != notified_socket:
                        clients_socket.send(message['r_header'] + message['r_data'] + message_connect_header + message_connect + user_disconnected['header'] + user_disconnected['data'])
                del clients[notified_socket]
                notified_socket.close()
                continue
    
            sender = clients[notified_socket]
            
            print(f"TCP: Recibiste un mensaje de {sender['data'].decode('utf-8')}")
            
            for client_socket in clients:
                receiver = clients[client_socket]
                if receiver['data'] == message['r_data']:
                    client_socket.send(sender['header'] + sender['data'] + message['m_header'] + message['m_data'])
                elif message['r_data'].decode('utf-8') == 'server':
                    if message['m_data'].decode('utf-8') == 'quit':
                        print(f"TCP: Por mensaje quit: Cerrando conexion de {clients[notified_socket]['data'].decode('utf-8')}")
                        sockets_list.remove(notified_socket)
                        #enviando mensaje de usuario desconectado
                        user_disconnected = clients[notified_socket]
                        message_connect ="user_disconnected"
                        message_connect = message_connect.encode('utf-8')
                        message_connect_header = f"{len(message_connect):<{HEADER_LENGTH}}".encode('utf-8')
                        for clients_socket in clients:
                            if clients_socket != notified_socket:
                                clients_socket.send(message['r_header'] + message['r_data'] + message_connect_header + message_connect + user_disconnected['header'] + user_disconnected['data'])
                        del clients[notified_socket]
                        notified_socket.close()
                        break
                elif  message['r_data'].decode('utf-8') == 'all':   
                    if client_socket != notified_socket:
                        client_socket.send(sender['header'] + sender['data'] + message['m_header'] + message['m_data'])
        
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        notified_socket.close()