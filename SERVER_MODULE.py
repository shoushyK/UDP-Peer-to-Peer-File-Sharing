import socket,pickle,time,random
from packet import Packet
from SOCKET_MODULE import MySocket

#class of servers to be instantiated. it uses SOCKET_MODULE class as well as the packet class
class Server():
    def __init__(self,my_ip): #set the IP of the server when instantiating
        print('Constructing a SERVER for peer...Loading')
        self.seq_num = 0 #server sequence number       
        self.expected_seq_num = 0 #expected sequence number
        self.your_ip = 0 #the ip to which this server will send to
        self.my_ip = my_ip #the IP of the server
        self.mySocket = self.createSocket(self.my_ip) #calling and creating a UDP socket
        
        self.dictionary = {} #dictionary that each server has, where it can store the client sequence number,its sequence number and the expected sequence number respectively
    
    def createSocket(self,port):
        x = MySocket() #instantiate a UDP socket object
        newSocket = x.create() #create a new UDP socket
        boundSocket = x.bind(newSocket, self.my_ip) #bind to the IP of the server
        return newSocket

    #getters
    def getMySocket(self):#get server socket
        return self.mySocket

    def get_my_ip(self):#get IP of server
        return self.my_ip
    
    #get sequence number
    def getseq_num(self):
        return self.seq_num

    #setters
    def set_your_ip(self,ip):#set IP of to which this server will send to 
        self.your_ip = ip
    
    #just like on the client's side, this function will generate a sequence number anywhere in between 10000 and 99999 with steps of 20
    def generateSeq(self):
        seq = random.randrange(10000,99999,20)
        self.seq_num = seq
        return seq
    
    #listening to incoming peers
    def listen(self):
        data, ip = self.mySocket.recvfrom(1024) #receive data and ip from client
        if ip in self.dictionary.keys(): #if this client IP already exists in my dictionary: then print already exits
            print('\nOld Peer connection')
        else:
            print('\nNew Peer connection') #else inform that it is a new connection
            recvd_packet = pickle.loads(data) #unpack the received packet
            seq_num = recvd_packet.seq_num #the sequence number of the received packet
            my_seq_num = self.generateSeq() #generate the server's sequence number specific to this client
            print('My sequence number for peer IP',ip,'is:',my_seq_num)
            self.dictionary[ip] = [seq_num, my_seq_num,0] #fill in the dictionary fields with calculated sequence numbers, initially the server does not expect a sequence number so the 3rd field is set to 0
        return data,ip
    
    #function that handles duplicates
    def handleDuplicates(self, recvd_packet, ip):
        replyPacket = Packet(self.dictionary[ip][1] ,'ack',True, recvd_packet.seq_num + 1) #
        self.mySocket.sendto(pickle.dumps(replyPacket),ip)

    #function to handle an expected packet (i.e. send an ACK for that packet)
    def handleExpectedPacket(self, recvd_packet,ip):
        self.dictionary[ip][1]+=1 #increment server sequence number
        replyPacket = Packet(self.dictionary[ip][1] ,'ack',True,recvd_packet.seq_num + 1) #create a reply packet which is an ack
        self.dictionary[ip][2] = self.dictionary[ip][1] + 1 #update the expected sequence number
        self.mySocket.sendto(pickle.dumps(replyPacket),ip) #send encoded packet (ACK)

    #function to close the server socket 
    def close(self):
        self.mySocket.close()