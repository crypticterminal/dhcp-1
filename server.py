import socket
import os
import copy
import sys
import numpy as np
ba = 0
na = 0
UDP_PORT=5000

def ip_string(ip_num):
    #convert the IP as a number to a string
    arr=[]
    for i in xrange(4):
        arr.append(ip_num%256)
        #print arr
        ip_num/=256
    arr.reverse()
    string=""
    for i in xrange(4):
        string+=str(arr[i])
        string+="."
    #print arr
    return string[:-1]

def allocate(ip_num, s):
    start=ip_num
    end=ip_num+s-1
    start_string=ip_string(start)
    end_string=ip_string(end)
    if end>ba or start>ba:
        end_string="-1"
    return start_string,end_string

#print ip_string(182206464)

f=open('subnets.conf','rb')
cidr=f.readline().split('\n')[0]
n=int(f.readline().split('\n')[0])
#print cidr,n
lab=[]
for i in xrange(n):
    lab.append(f.readline().split('\n')[0].split(':'))
lab = np.array(lab)
lab = lab[np.argsort(lab[:,1])]
lab = lab[::-1]

lab_name = lab[:,0]
lab_cap = lab[:,1]
lab_cap = lab_cap.astype(int)
for i in xrange(n):
    lab_cap[i] = lab_cap[i] + 2
    lab_cap[i] = (lab_cap[i]-1).bit_length()

cidr = cidr.split('/')
subnet = int(cidr[1])
cidr = cidr[0].split('.')
local = 0
x = 0
for i in xrange(4):
    x = x*256
    x+=int(cidr[i])

subnet_number = (2**33)- (2**(32-subnet))
#print subnet_number
#print x
na = subnet_number&x
ba = x|((2**(32-subnet))-1)
#print na
#print ba
nat=na

addresses=[]

for i in xrange(n):
    size=2**lab_cap[i]
    natt=copy.deepcopy(nat)
    sizet=copy.deepcopy(size)
    sa,ea=allocate(natt,sizet)
    gw=ip_string(natt+1)
    nat+=size
    #print str(sa+'/'+str(lab_cap[i]))
    #print sa,ea,gw
    addresses.append([sa,ea,gw,lab_cap[i]])

#print addresses

MAC={}
IP={}

for i in xrange(n):
    mac=f.readline().split('\n')[0].split(' ')
    MAC[mac[0]]=mac[1]
    IP[lab_name[i]]=addresses[i]

print MAC
print IP

#ranges contain the range of left IP address that can be assigned to a system for each lab
ranges = {}

for name in lab_name:
    print name
    s = IP[name][0].split('.')
    e = IP[name][1].split('.')
    sx = 0
    ex = 0
    for i in xrange(4):
        sx = sx*256
        ex = ex*256
        sx += int(s[i])
        ex += int(e[i])
    ranges[name] = [sx,ex,sx+2] # sx+1 is dns and gateway

ranges["left"] = [ranges[lab_name[-1]][1]+1, ba, ranges[lab_name[-1]][1]+3]

print ranges
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data,addr
    tosend = ""
    lab = ""
    if data in MAC:
        lab = MAC[data]
    else:
        if data == "single_IP":
            lab = "left"
        else:
            lab = "unvalid MAC"
    print lab
    if lab == "unvalid MAC":
        tosend = "Enter a valid MAC Address"
    else:
        if ranges[lab][2] > (ranges[lab][1]-1):
            tosend = "IP address cannot be allocated : User count exceeded"
        else:
            tosend += ip_string(ranges[lab][2]) + "\n"
            ranges[lab][2] += 1
            tosend += ip_string(ranges[lab][0]) + "\n"
            tosend += ip_string(ranges[lab][1]) + "\n"
            tosend += ip_string(ranges[lab][0] + 1) + "\n"
            tosend += ip_string(ranges[lab][0] + 1) + "\n"
    sock.sendto(tosend, addr)
