import socket,pickle,time,random
from packet import Packet

#class client that uses packet class
class Client():
    def __init__(self):
        
        self.seq_num = 0 #client's sequence number        
        self.expected_seq_num = 0 #expected sequence number'
        self.your_ip = 0 #the ip to which this client will send to
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #creating a client UDP socket

        self.your_seq_num = -1
        print('Constructing a CLIENT for peer...Loading')

    #getters
    def getMySocket(self): #get socket
        return self.mySocket
    
    def getseq_num(self): #get sequence number
        return self.seq_num

    #setters
    def set_your_ip(self,ip): #set IP to which client will send to
        self.your_ip = ip

    def setTimeout(self,timeout): #setting the timeout
        self.mySocket.settimeout(timeout)

    #function that generates a random sequence number anywhere between 10000 and 99999 with steps of 20
    def generateSeq(self): #
        seq = random.randrange(10000,99999,20)
        self.seq_num = seq #set the sequence number to this randomly generated one
        self.expected_seq_num = self.seq_num+1 #expected sequence number is the sequence number +1
        print('Packet sequence number is:', seq)
        return seq
    
    def createPacket(self, msg, mySeq , yourSeq): #function to create a packet
        packet = Packet(mySeq,msg,False,yourSeq) #this packet is not an ACK
        return packet
    
    def sendPacket(self, packet): #function to send a packet
        try:
            self.mySocket.sendto(pickle.dumps(packet), self.your_ip) #send the encoded packet to the address of the sender, flag bit default set to 0 (function sendto(bytes, flags, address)) 
        except socket.error: #handle error
            print('Error_05: cannot SEND packet')

    def listen(self): #function to receive incoming packet and IP
        data, ip = self.mySocket.recvfrom(1024)
        return data,ip

    def handleAcks(self,recvd_packet): #function to handle acks
        self.your_seq_num = recvd_packet.seq_num
        self.seq_num+=1 #increment the sequence number 
        self.expected_seq_num+=1 #increment the expected sequence number
    
    def handleTimeout(self, packet): #function to handle timeout
        self.mySocket.sendto(pickle.dumps(packet),self.your_ip)