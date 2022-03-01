#imports
import socket
import errno
import sys 
#defining header_length
HEADER_LENGTH = 10
#saving IP and PORT numbers to variables
IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")
#creating socket with AF_INET address family (other possibilities are AF_BLUETOOTH, AF_INET6, etc.)
#using SOCK_STREAM, which allows for TCP (transmission control protocol) to break data into transmittable packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect to some IP and some PORT
client_socket.connect((IP, PORT))
#set client_socket not to disallow connections
client_socket.setblocking(False)
#encode and send user header and username
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
#wait for message input
while True:
    message = input(f'{my_username}: ')
    #if the message isn't empty, send to server
    if message:
        #encode and send header and message 
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
    try:
        while True:
            #received username header of length 10 (constant; we defined this above)
            username_header = client_socket.recv(HEADER_LENGTH)
            #if the username header isn't equal to HEADER_LENGTH, it means the server closed the connection; we can exit
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            #turn header into int
            username_length = int(username_header.decode('utf-8').strip())
            #receive username, decode username, and save it in a variable called 'username'
            username = client_socket.recv(username_length).decode('utf-8')
            #turn header into int, decode message, and receive the message, saving it in a variable called 'message'
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            #finally, print message from our user!
            print(f'{username}: {message}')     
    #handle exceptions
    except IOError as e:
        #if there is no incoming data, continue without closing the connection; otherwise, close the connection
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Error: {}'.format(str(e)))
            sys.exit()
        continue
    #handle any other exception by exiting the system
    except Exception as e:
        print('Error: '.format(str(e)))
        sys.exit()