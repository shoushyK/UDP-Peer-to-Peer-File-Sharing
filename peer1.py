import socket,os,pickle,time,random,csv
from packet import Packet
from SERVER_MODULE import Server
from datetime import datetime
from SOCKET_MODULE import MySocket
from CLIENT_MODULE import Client
from threading import Thread

def sending(x):
    port = 12340                
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             
    host = "127.0.0.1"   
    s.bind((host, port))            
    s.listen(5)                    

    print ('Server listening....')

    conn, addr = s.accept()   
    print ('Got connection from', addr)
    data = conn.recv(4096)
    print('Server received', repr(data))

    filename=x         
    f = open(filename,'rb')
    l = f.read(4096)
    while (l):
        conn.send(l)
        print('Sent ',repr(l))
        l = f.read(4096)
    f.close()

    print('Done sending')
    conn.send('Thank you for connecting'.encode())
    conn.close()

def rec(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                
    host = "127.0.0.1"  
    port = 12345                    
    s.connect((host, port))
    s.send("Hello server!".encode())

    with open('received_file_from_peer2', 'wb') as f:
        print ('file opened')
        while True:
            print('receiving data...')
            data = s.recv(4096)
            print('data=%s', (data))
            if not data:
                break
            # write data to a file
            f.write(data)

    f.close()
    print('Successfully get the file')
    s.close()
    print('connection closed')

class Client_SGO(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        total_time = datetime.now()
        myClient = Client()
        myClient.generateSeq()
        myClient.set_your_ip(("127.0.0.1", 9999)) #sending
        myClient.setTimeout(2)
        packetsSent = 0
        packetsReceived = 0
        number_lines = 0
        while True:
            print("Type sr for sending files, otherwise continue sending message: ")
            reply = input("\n------------------------------------------------------------\nPeer>")
            if (reply=='sr'):
                qz = input("\n------------------------------------------------------------\nType the name of the file you want to send or type n/a for receiving file from the other peer > " )
                if (qz == "n/a"):
                    rec()
                else:    
                    sending(qz)
            else:
                
                packet = myClient.createPacket(reply, myClient.getseq_num(), myClient.your_seq_num+1)
                myClient.sendPacket(packet)
                packetsSent+=1
                received = False
                while received == False:
                    try : 
                        data,ip = myClient.mySocket.recvfrom(6000)
                        recvd_packet = pickle.loads(data)
                        
                        print('Received a packet having my seq no',recvd_packet.your_seq_num,'server seq no:',recvd_packet.seq_num)
                        print('Expected seq no',myClient.expected_seq_num)
                        if myClient.expected_seq_num == recvd_packet.your_seq_num:
                            
                            print('Acked')
                            packetsReceived+=1
                            received = True
                            myClient.handleAcks(recvd_packet)

                    except socket.timeout :
                        print("Message is retransmitting...")
                        myClient.handleTimeout(packet)
                        packetsSent+=1 
                print('Packets sent:', packetsSent)
                print('Packets received:',packetsReceived)
                total_time_str = str((datetime.now() - total_time).total_seconds())
                filename = 'results/packet_corruption/corrupt_80%_client.txt'
                fields=[packetsSent, packetsReceived]
                lines = open(filename, 'r').readlines()        
                file_row = str(packetsReceived) + "," + str(packetsSent) + ","

                out = open(filename, 'w+')
                out.writelines(file_row)
                out.writelines(total_time_str)
                out.close()
            


def main():
    myServer = Server(6000)
    myServer.generateSeq()
    packetsReceived = 0
    packetsSent = 0
    print('Listening on socket port', myServer.get_my_ip())
    while True:
        data,ip = myServer.listen()
        recvd_packet = pickle.loads(data) #converting python into byte stream object (instead of using data.decode() or data.encode())
        myServer.set_your_ip(ip)
        print('\n------------------------------------------------------------\nReceived a packet.Client ip : ', ip)
        print('Server seq no',recvd_packet.your_seq_num)
        print('Client seq no',recvd_packet.seq_num)
        print('Expected seq no',myServer.dictionary[ip][2])
                      

        if myServer.dictionary[ip][2] == recvd_packet.your_seq_num:
            f = open("peer_sent_messages/"+str(ip[0])+ "_" + str(ip[1]) + ".txt","a+")
            f.write(recvd_packet.payload + "\n")
            f.close()            
            packetsReceived += 1
            print('Message from client',recvd_packet.payload)
            myServer.handleExpectedPacket(recvd_packet, ip)
            packetsSent+=1
            
        elif myServer.dictionary[ip][2] > recvd_packet.your_seq_num:
            print('Duplicate packet detected: ', recvd_packet.payload)
            myServer.handleDuplicates(recvd_packet, ip)
            packetsReceived += 1
            packetsSent+=1

        file_name = 'results/packet_corruption/corrupt_80%.txt'
        lines = open(file_name, 'r').readlines()        
        lines[0] = str(packetsReceived) + "," + str(packetsSent) 

        out = open(file_name, 'w+')
        out.writelines(lines)
        out.close()

if __name__ == '__main__':
    t1 = Client_SGO()
    t1.start()
    main()
