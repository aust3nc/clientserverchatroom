#imports
import socket
import select
#defining header_length 
HEADER_LENGTH = 10
#saving IP and PORT numbers to variable
IP = "127.0.0.1"
PORT = 1234
#creating socket with AF_INET address family (other possibilities are AF_BLUETOOTH, AF_INET6, etc.)
#using SOCK_STREAM, which allows for TCP (transmission control protocol) to break data into transmittable packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#setting socket option to 'REUSEADDR' and socket level to 'SOL_SOCKET'
#'REUSEADDR' allows us to listen for connections and bind to client-side sockets
#'SOL_SOCKET' tells the socket that the layer it's working within the scope of the overall application
#is the socket, or networking layer
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#binding to our IP and PORT
server_socket.bind((IP, PORT))
#listening for client connections
server_socket.listen()
#instantiating a list of sockets for select.select(); so far, we only have our server socket
sockets_list = [server_socket]
#instantiating an empty dictionary for our list of clients
clients = {}
#printing a message to console so that the user knows the program is working...
print(f'Listening for connections on {IP}:{PORT}...')
#defining a function which allows the server side to receive messages from client sockets
def receive_message(client_socket):
    try:
        #receive header with length of 10
        message_header = client_socket.recv(HEADER_LENGTH)
        #otherwise, the client already closed the connection
        if not len(message_header):
            return False
        #decode header
        message_length = int(message_header.decode('utf-8'))
        #return bundled message object 
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        #an empty message was received, meaning the client accidentally closed the connection
        return False
#use OS select() to select three sockets: 
#rlist (read list) are sockets the server needs to listen for
#wlist (write list) are sockets the server needs to send data to
#xlist (exception list) are sockets we are watching for errors
while True:
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)
    #loop over our list of sockets to listen for
    for notified_socket in read_sockets:
        #if the client is in our list of sockets to watch out for...
        if notified_socket == server_socket:
            #connect to the client!
            client_socket, client_address = server_socket.accept()
            #receive username
            username = receive_message(client_socket)
            #if the user doesn't input a name...
            if username is False:
                continue
            #add to the read/exception list anyway and continue to monitor
            sockets_list.append(client_socket)
            #save name as the client at the index of the current socket as the value in our clients dictionary 
            clients[client_socket] = username
            print('Someone connected')
        #otherwise, receive message from client
        else:
            message = receive_message(notified_socket)
            #if there is no message, it means our client disconnected
            if message is False:
                print('Someone disconnected')
                #remove the client from our list of sockets, as they are no longer online
                sockets_list.remove(notified_socket)
                #also remove client from our list of users
                del clients[notified_socket]
                continue
            #get username
            username = clients[notified_socket]
            #print message from user!
            print(f'{username["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            #send message to everyone on the server besides the user who sent it
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(username['data'] + username['header'] + message['data'])
                    
