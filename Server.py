import socket
import threading
import os
import shlex
import hashlib
import pickle
import time
import platform
import datetime

global linked_list

count=0
peer_list=list()
index_list=list()
rfcList=list()
lock = threading.Lock()
OS = platform.platform()
datetime = time.strftime("%a, %d %b %Y %X %Z")

class PeerRecord:
    def __init__(self,peerid=None,peerIPaddr='None',peerPort='None',flag=0,TTL=0):
        self.peerid=peerid
        self.peerIPaddr=peerIPaddr
        self.peerPort=peerPort
        self.flag=flag
        self.TTL=TTL        

    def __str__(self):
        return str(self.peerid)+' '+str(self.peerIPaddr)+' '+str(self.peerPort)+' '+str(self.flag)+' '+str(self.TTL)

    def getpeerid(self):
        return self.peerid

    def getpeerdata(self):
        return [str(self.peerid),str(self.peerIPaddr),str(self.peerPort),str(self.flag),str(self.TTL)]

class Node:
    def __init__(self, data, next_node=None):
        self.data = data
        self.next_node = next_node

    def getData(self):
        return self.data

#create the structure to hold information about the list
#including methods to append or remove a Node
class LinkedList:

    def __init__(self):
        self.head = Node(None, None)

    def getHead(self):
        return self.head

    def append(self, data):
        cur_node = self.head
        while(cur_node.next_node is not None):
            cur_node = cur_node.next_node
        cur_node.next_node = Node(data)

    def remove(self, value):
        prev_node = self.head
        cur_node = prev_node.next_node

        while(cur_node):
            data = cur_node.data
            if data:
                if ip == data[2] and int(port) == int(data[3]):
                    if prev_node:
                        prev_node.next_node = cur_node.next_node
                    else:
                        self.head=cur_node.next_node
                    return True
                    if (cur_node.next_node == None):
                        break
            prev_node = cur_node
            cur_node = cur_node.next_node
        return False

    def printList(self):
        cur_node = self.head
        
        while(cur_node.next_node):
            Print( cur_node.data)
            cur_node = cur_node.next_node
        #print cur_node.data

    def printData(self, value):
        cur_node = self.head
        #cur_node = cur_node.next_node
        if cur_node.next_node is not None:
            cur_node = cur_node.next_node
            while(True):
                data1 = cur_node.data
                if (data1[0] == value):
                    return data1
                if (cur_node.next_node == None):
                    break
                cur_node = cur_node.next_node
        return None

    def findNode(self, value):
        cur_node = self.head
        cur_node = cur_node.next_node
        data1 = []
        while(True):
            data1 = cur_node.data
            if (data1[0] == value):
                return data1
            if (cur_node.next_node == None):
                break
            cur_node = cur_node.next_node
         #return None

    def UpdateFlag(self, value):
        cur_node = self.head
        cur_node = cur_node.next_node
        data1 = []
        while(True):
            data1 = cur_node.data
            if (int(data1[0]) == int(value)):
                data1[3] = 0
                data1[4] = 0
                Print( data1)
                return data1
            if (cur_node.next_node == None):
                break
            cur_node = cur_node.next_node
        return None


    def findActiveNode(self):
        a = []
        data1 = []
        cur_node = self.head
        cur_node = cur_node.next_node
        while(True):
            data1 = cur_node.data
            if (data1[3] == '1'):
                a.append(data1)
            if (cur_node.next_node == None):
                break
            cur_node = cur_node.next_node
        return a


def add_peer_to_list(data):
    global count
    global linked_list
    count = count+1
    a=data

    flag = 1
    TTL = 30
    nodedata = PeerRecord(a[0],a[1],a[2],flag,TTL)
    data1 = nodedata.getpeerdata()
    linked_list.append(data1)

    code = '200'
    phrase = 'Registered Successfully'

    return code, phrase


def CalculateHash(hashdata):
    md5 = hashlib.md5()
    md5.update(hashdata)
    digest = md5.hexdigest()
    hash_val = int(digest, 16)
    hash_value = str(hash_val)
    
    return hash_value[:3]

def handlePeer(data,clientsocket,clientaddr):
    global count
    global TTL
    Print( "***********************************")
    Print( "Request received from Client :")
    PrintRequest(data)
    Print( "***********************************")
    
    rlist = data
    if rlist[0] == 'REGISTER':
        client_id=CalculateHash((rlist[3]+":"+rlist[5]))
        code, phrase=add_peer_to_list([client_id,rlist[3],rlist[5]])
     
        response=["P2P-DI/1.0 ",str(code),str(phrase),"Client-ID: ",str(client_id)]
        clientsocket.send(pickle.dumps(response))

    elif rlist[0] == 'PQUERY':
        index_list = linked_list.findActiveNode()
        code = '200'
        phrase = 'OK'
        
        response = ["P2P-DI/1.0 ",str(code),str(phrase),"INDEX-LIST: ",index_list]
        clientsocket.send(pickle.dumps(response))

    elif rlist[0] == 'LEAVE':
        client_id = rlist[1]
        Print(client_id)
        client = client_id[0]
        value=linked_list.UpdateFlag(client)
        
        Print(['Updated the flag to inactive. ',value])
        response = 'You can leave the Torrent. Thank You!'
        clientsocket.send(pickle.dumps(response))

    elif rlist[0] == 'KEEPALIVE':

        response = 'Keep alive received.'
        clientsocket.send(pickle.dumps(response))
    

def handler(clientsocket, clientaddr):

    data = clientsocket.recv(1024)
    data = pickle.loads(data)
    cur_thread=threading.current_thread()
    handlePeer(data,clientsocket,clientaddr)



def Print(data):
    lock.acquire()
    print data
    lock.release()

def PrintRequest(message):
        
    if message[0] == 'REGISTER':
        message = "REGISTER P2P-DI/1.0 \nHost: "+str(message[3])+"\nPort: "+str(message[5])+"\nOS: "+OS

    if message[0] == 'PQUERY':
        message = "PQUERY P2P-DI/1.0 \nClient ID: "+ str(message[2])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS

    if message[0] == 'KEEPALIVE':
        message = "KEEPALIVE "+str(message[1])+ " " + str(message[2]) +" P2P-DI/1.0 \nClient ID: "+ str(message[1])+" \nHost: "+str(message[5])+"\nPort: "+str(message[7])+"\nOS: "+ OS

    if message[0] == 'LEAVE':
        a = message[1]
        message = "LEAVE "+str(message[1])+ " " + str(message[2]) +" P2P-DI/1.0 \nClient ID: "+ str(a[0])+" \nHost: "+str(message[5])+"\nPort: "+str(message[7])+"\nOS: "+ OS

    Print(message)


        
if __name__=="__main__":
    global linked_list
    global TTL
    linked_list=LinkedList()
    print "Enter the IP address of Server:"
    IP=raw_input()
    #IP = '192.168.1.110'
    #IP = '10.139.67.84'
    #Print( IP)
    Print( "Enter the Port of Server:")
    #IP='127.0.0.1'
    PORT=int(raw_input())
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((IP,PORT))

    serversocket.listen(20)

    Print( "Server is listening for connection \n")
    
    while(1):
        #print "Server is listening for connection \n"

        clientsocket, clientaddr = serversocket.accept()
        serverThread = threading.Thread(target=handler, args=(clientsocket,clientaddr))
        serverThread.start()

        
    serversocket.close()
