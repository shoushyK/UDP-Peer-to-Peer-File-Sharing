README
READ ME FILE 

The project was built using Python as the programming language and Ubuntu 20.4 as the operating system  

The application is a peer to peer chatting application that allows file sharing and direct message sending on both ends. The chat messages are made to be sent via an application-layer reliable UDP connection and file sharing via a separate TCP connection. 

The python libraries needed for running the code are: 

Os-Socket-Pickle-Time-Random  

For testing, use the netem tool, in the Linux terminal, to simulate packet loss: 

	-The ‘lo’ in the command here refers to the localhost 

	- Sudo tc qdisc add dev lo root netem loss 70%  
	- Feel free to use any other netem command such as simulating delays

 (This causes 70% of the packets sent from one peer to the other to be randomly and purposefully dropped) 

For the application to function follow the steps below: 

1) After downloading the file unzip it 

2) open the file directory in the termial  

3) write python3 peer1.py and peer2.py on separate terminals (make sure to open the terminal from the directory of the zip file of the code)
4) write "c" or "sr" to send a message or file respectively on BOTH peers (terminals)
5) if a peer is sending a file, input the file name on the sending side/peer and "n/a" on the receiving side/peer of the file
6) to exit the program: write ctrl+z (centinel) 