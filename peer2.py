import socket,os,pickle,time,random,csv
from packet import Packet
from SERVER_MODULE import Server
from datetime import datetime
from SOCKET_MODULE import MySocket
from CLIENT_MODULE import Client
from threading import Thread

def sending(x): #function that sends a file over a TCP socket
    port = 12345 #port number (chosen randomly within the scope of available ports)                  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating a TCP socket             
    host = "127.0.0.1" #IP of local network interface 
    s.bind((host, port)) #binding the IP to the port           
    s.listen(5) #listening, the argument passed into .listen() is the backlog which specifies the maximum number of queued connections (at least 1)               

    print ('Listening for a TCP connection....') #print message

    conn, addr = s.accept() #accept the connection and address    
    print ('Received a connection from', addr)
    data = conn.recv(4096) #the data that is received
    print('The peer received: ', repr(data)) #The repr() function returns a printable string of the given object

    filename=x          
    f = open(filename,'rb') #"rb" mode opens the file in binary format for reading
    l = f.read(4096) #read the file with buffer size 4096, i.e. until you have at most 4096 characters from stream
    while (l): #while there is data to read from the file:
        conn.send(l) #send this data to the connection established and already accepted
        print('What is sent: ',repr(l)) #print what is sent on the console
        l = f.read(4096) #continue reading 
    f.close() #close the file when there is nothing left to read

    print('Finished Sending')
    conn.send('Finished Sending File!'.encode())
    conn.close()

def rec(): #function that receives a file over a TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #port number of the receiver socket (chosen randomly within the scope of available ports)         
    host = "127.0.0.1" #IP of local network interface  
    port = 12340 #port number (chosen randomly within the scope of available ports)                     

    s.connect((host, port))
    s.send("Hello Sender!".encode())

    with open('received_file_from_peer1', 'wb') as f: #"wb" mode opens the file in binary format for writing.
        print ('Opening File...') #print message
        while True: #print while receiving data from the file
            print('Receiving Data from file...')
            data = s.recv(4096) #receive at a buffer size of 4096
            print('Data: ', repr(data)) #printing the data in a readable form
            if not data: #if there is no more data left to be received, break
                break
            f.write(data) #writing received data to the file "received_file_from_peer1"

    f.close() #close file
    print('File reception completed successfully')
    s.close()
    print('Connection closed')

class Client_SGO(Thread): #client thread
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        total_time = datetime.now() #starting from when the client thread was started, to count the time
        myClient = Client()
        myClient.generateSeq()
        myClient.set_your_ip(("127.0.0.1", 6000)) #sending
        myClient.setTimeout(2) #set timeout to 2 seconds
        packetsSent = 0 #keep track of packets sent
        packetsReceived = 0 #keep track of packets received
        number_lines = 0
        while True:
            reply = input("\n------------------------------------------------------------\nPeer>")
            if (reply=='sr'):
                qz = input("\n------------------------------------------------------------\nType the name of the file you want to send or type n/a for receiving file from the other peer > " )
                if (qz == "n/a"):
                    rec()
                else:    
                    sending(qz)
            else:
                packet = myClient.createPacket(reply, myClient.getseq_num(), myClient.your_seq_num+1) #create a packet with the entered input
                myClient.sendPacket(packet) #send this packet to the other peer
                packetsSent+=1 #increment number of packets sent
                received = False #haven't received an ack yet
                while received == False: #while haven't received the ack for this packet
                    try : 
                        data,ip = myClient.mySocket.recvfrom(6000) #try listening for incoming data
                        recvd_packet = pickle.loads(data) #load that data
                        
                        print('Received a packet having my seq no',recvd_packet.your_seq_num,'server seq no:',recvd_packet.seq_num)
                        print('Expected seq no',myClient.expected_seq_num)
                        if myClient.expected_seq_num == recvd_packet.your_seq_num: #if my expected sequence number matches to received packet's sequence number
                            
                            print('Acked')
                            packetsReceived+=1 #increment packets received
                            received = True #break out of the while loop 
                            myClient.handleAcks(recvd_packet)  #then i have an ACK for my message

                    except socket.timeout : #when there's a timeout: i have to resend my message
                        print("Message is retransmitting...")
                        myClient.handleTimeout(packet)
                        packetsSent+=1 
                print('Packets sent:', packetsSent)
                print('Packets recvd:',packetsReceived)

                #the following lines are for the purposes of recording the corrupt/lost packets
                total_time_str = str((datetime.now() - total_time).total_seconds())
                filename = 'results/packet_corruption/corrupt_80%_client.txt'
                fields=[packetsSent, packetsReceived]
                lines = open(filename, 'r').readlines()        
                file_row = str(packetsReceived) + "," + str(packetsSent) + ","

                out = open(filename, 'w+')
                out.writelines(file_row)
                out.writelines(total_time_str)
                out.close()

            #if the user wanted to send a file:
            


def main(): #the server side
    myServer = Server(9999) #instantiate a server on port 9999 (chosen randomly within the scope of available ports)
    myServer.generateSeq() #generate a random sequence number
    packetsReceived = 0 #keep a record of received packets
    packetsSent = 0 #keep a record of sent packets
    print('Listening on socket port', myServer.get_my_ip()) #print listening socket port
    while True: #always listening
        data,ip = myServer.listen() #get the data and ip of the incoming connections
        recvd_packet = pickle.loads(data) #converting python into byte stream object (instead of using data.decode() or data.encode())
        myServer.set_your_ip(ip) #set the IP of the receiver
        print('\n------------------------------------------------------------\nReceived a packet from : ', ip)
        print('Server sequence number',recvd_packet.your_seq_num)
        print('Client sequence number',recvd_packet.seq_num)
        print('Expected sequence number',myServer.dictionary[ip][2]) #get expected sequence number from the dictionary of the server at the 3rd index
                      

        if myServer.dictionary[ip][2] == recvd_packet.your_seq_num: #if the sequence number of the received packet and the expected sequence number match
            f = open("peer_sent_messages/"+str(ip[0])+ "_" + str(ip[1]) + ".txt","a+") #write into a file to keep track of sent message records
            f.write(recvd_packet.payload + "\n") 
            f.close()            
            packetsReceived += 1 #increment packets received
            print('Message from peer:',recvd_packet.payload) #displays the message received
            myServer.handleExpectedPacket(recvd_packet, ip) #handles the expected packet specific to this peer
            packetsSent+=1 #increments packets sent
            
        elif myServer.dictionary[ip][2] > recvd_packet.your_seq_num: #if duplicate message is caught
            print('Duplicate packet detected: ', recvd_packet.payload)
            myServer.handleDuplicates(recvd_packet, ip) 
            packetsReceived += 1
            packetsSent+=1

        #the following lines are for the purposes of recording the corrupt/lost packets
        file_name = 'results/packet_corruption/corrupt_80%.txt'
        lines = open(file_name, 'r').readlines()        
        lines[0] = str(packetsReceived) + "," + str(packetsSent) 

        out = open(file_name, 'w+')
        out.writelines(lines)
        out.close()


if __name__ == '__main__': 
    t1 = Client_SGO() #instantiating and starting the Client thread
    t1.start() 
    main()
