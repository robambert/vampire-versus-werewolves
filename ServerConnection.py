# -*- coding: utf-8 -*-
import socket
import struct

class ClientThread():
    def __init__(self):
        self.serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serverSocket.setblocking(True)

    def connect(self, ip, port, name = "StupidAI"):
        self.serverSocket.connect((ip,port))
        print("Connection to %s on port %s" %(ip,port))
        data=name
        return self.send(["NME",len(data),data])    

    def receive_data(self, size, fmt):
        data = bytes()
        while len(data) < size:
            data += self.serverSocket.recv(size - len(data))
        return struct.unpack(fmt, data)

    def receive(self, expected):
        received = self.serverSocket.recv(3).decode("ascii") 
        if received==expected or received=="END" or received=="BYE":  
            if received=="SET":
                n,m=self.receive_data(2,"2B")
                return [(n,m)]+self.receive("HUM")
            elif received=="HUM":
                res=[]
                n= self.receive_data(1,"1B")[0]
                homes= self.receive_data(2*n,"{}B".format(2*n))
                count=0
                prev=0
                for h in homes:
                    if count%2==0:
                        prev=h
                    else:
                        res.append((prev,h))
                    count+=1
                return [n]+res+self.receive("HME")
            elif received=="HME":
                start_pos=tuple(self.receive_data(2,"2B"))
                return [start_pos]+self.receive("MAP")
            elif received=="MAP" or received=="UPD":
                n=self.receive_data(1,"1B")[0]
                commands=self.receive_data(5*n,"{}B".format(5*n))
                res=[]
                x=0
                y=0
                h=0
                v=0
                count=0
                for c in commands:
                    if count%5==0:
                        x=c
                    elif count%5==1:
                        y=c
                    elif count%5==2:
                        h=c
                    elif count%5==3:
                        v=c
                    else:
                        res.append((x,y,h,v,c))
                    count+=1
                return res
            elif received=="END":
                return 1
            else:
                self.serverSocket.close()
                return 2
        else:
            print("Error at "+expected)
            return 0

    def send(self, data):
        if data[0]=="NME":
            self.serverSocket.send(data[0].encode("ascii"))
            self.serverSocket.send(struct.pack("1B",data[1]))
            self.serverSocket.send(data[2].encode("ascii"))
            return self.receive("SET")
        elif data[0]=="MOV":
            self.serverSocket.send(data[0].encode("ascii"))
            n=data[1]
            self.serverSocket.send(struct.pack("1B",n))
            self.serverSocket.send(struct.pack("{}B".format(5*n), *(data[2])))
            return self.receive("UPD")