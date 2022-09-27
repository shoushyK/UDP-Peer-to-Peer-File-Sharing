import socket,os,pickle,time,random
from packet import Packet

#class socket
class MySocket():
    def __init__(self):
        print('Constructing a SOCKET...Loading')
    
    def create(self):
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
        except socket.error:
            print("Error_01: cannot CONNECT to UDP socket")
            exit()
    
        return my_socket

    def bind(self, mySocket, port):
        try:
            mySocket.bind(("", port))
        except socket.error:
            print('Error_02: cannot BIND to socket port ',port)
        return mySocket
         
    
    
