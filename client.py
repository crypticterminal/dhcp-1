import sys
import socket

UDP_PORT = 5000
MESSAGE = "Hello, World!"

flag = 0


if len(sys.argv)==1:
    MESSAGE="single_IP"
    flag = 1
elif len(sys.argv)==3:
    if sys.argv[1] == "-m":
        flag = 1
    MESSAGE=sys.argv[2]

#print MESSAGE

if flag == 0:
    print "Enter Valid format"
else:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(MESSAGE, ('255.255.255.255', UDP_PORT))
    data, addr = sock.recvfrom(1024)
    print data,addr
