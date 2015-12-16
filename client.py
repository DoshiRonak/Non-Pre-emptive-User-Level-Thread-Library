import socket
import threading
import os
import shlex
import hashlib
import pickle
import time
import sys
import platform
from tabulate import tabulate
from mimetypes import MimeTypes

global Predecessor
global PPredecessor
global Successor
global LRFCdata
global BackupRFCdata
global DHTheader
global localheader
global OS
global datetime
global linked_list
global Local_linked_list
global bkp_linked_list

HOST=''
IP=''
PORT=0
pred = []
Psucc = []
Ppred = []
DHTheader =['File id', 'File Name','Peer IP','Peer Port']
localheader =['File id', 'File Name']
LRFCdata = []
BackupRFCdata = []
Successor = []
Predecessor = []
PPredecessor = []
lock = threading.Lock()

OS = platform.platform()
datetime = time.strftime("%a, %d %b %Y %X %Z")

class RFCRecord:
    def __init__(self,rfc_id=-1,rfc_title='None',peerip=-1,peerport=-1):
        self.rfc_id=rfc_id
        self.rfc_title=rfc_title
        self.peerip=peerip
        self.peerport=peerport

    def __str__(self):
        return str(self.rfc_id)+' '+str(self.rfc_title)+' '+str(self.peerip)+' '+str(self.peerport)

    def getrfc_record(self):
        return [str(self.rfc_id),str(self.rfc_title),str(self.peerip),int(self.peerport)]


class LocalRFCRecord:
    def __init__(self, rfc_id, rfc_title):
        self.rfc_id = rfc_id
        self.rfc_title = rfc_title
    def getLocalRFC(self):
        data = [self.rfc_id, self.rfc_title]
        return data


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

    def remove(self, ip,port):        
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


    def Filter(self,pred_id,succ_id,my_id):
        filterdata=[]
        pred_id=int(pred_id)
        succ_id=int(succ_id)
        my_id=int(my_id)
        prev_node = self.head
        cur_node = self.head.next_node

        while(cur_node):
            data = cur_node.data
            fileid=int(data[0])
            if my_id < pred_id:
                if my_id < fileid and pred_id > fileid:
                    filterdata.append(data)
                    prev_node.next_node = cur_node.next_node
                    cur_node = cur_node.next_node
                else:
                    prev_node = cur_node
                    cur_node = cur_node.next_node

            else:
                if (my_id < fileid and pred_id < fileid) or (my_id > fileid and pred_id >= fileid):
                    filterdata.append(data)
                    prev_node.next_node = cur_node.next_node
                    cur_node = cur_node.next_node
                else:
                    prev_node = cur_node
                    cur_node = cur_node.next_node

        if (filterdata):
            return filterdata
        else:
            return None

    def printList(self,header):
        a=[]
        cur_node = self.head
        if cur_node.next_node is not None:
            
            cur_node = cur_node.next_node
            while(cur_node.next_node):
                a.append(cur_node.data)
                cur_node = cur_node.next_node
            a.append(cur_node.data)  
            DHTtable=tabulate(a, headers=header,tablefmt='grid')
            Print(DHTtable)
        else:
            Print('No data in DHT')

    def printData(self, value):
        cur_node = self.head
        cur_node = cur_node.next_node
        if cur_node.next_node is not None:
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

    def findData(self, value):
        cur_node = self.head
        if cur_node.next_node is not None:
            cur_node = cur_node.next_node
            while(True):
                data1 = cur_node.data
                if (data1 == value):
                    return data1
                if (cur_node.next_node == None):
                    break
                cur_node = cur_node.next_node
        return None

    def sort(self):
        if self.head and self.head.next_node:
            i = self.head
            while i.next_node:
                selected = i
                j = i.next_node
                while j:
                    if j.data < selected.data:
                        selected = j
                    j = j.next_node
                if not selected==i:
                    i.data, selected.data = selected.data, i.data
                i = i.next_node


    def Removedups(self):

        prev_node = self.head
        cur_node = self.head.next_node
        
        while(prev_node.next_node):
            if (prev_node.data == cur_node.data):
                prev_node.next_node = cur_node.next_node
                if (cur_node.next_node == None):
                    break
            prev_node = cur_node
            cur_node = cur_node.next_node

    def Empty(self):
        cur_node = self.head
        cur_node.next_node = None

    def DHTdata(self):
        a=[]
        cur_node = self.head
        if cur_node.next_node is not None:
            
            cur_node = cur_node.next_node
            while(cur_node.next_node):
                a.append(cur_node.data)
                cur_node = cur_node.next_node
            a.append(cur_node.data)
        if (a):
            return a
        else:
            return None


def initial_rfc_add():
    global LRFCdata
    global Local_linked_list
    
    file_list = os.listdir(os.getcwd())
    local_temp_rfc = list()
    for file_name in file_list:
        files = file_name.split(".")
        if files[1] == "pdf":
            rfc_title = str(files[0])
            rfc_id = CalculateHash(rfc_title)
            LocalRFC = LocalRFCRecord(rfc_id, rfc_title)
            LRFCdata.append(LocalRFC.getLocalRFC())
            Local_linked_list.append(LocalRFC.getLocalRFC())
            
    return LRFCdata


def new_rfc_add():
    newLRFCdata = []
    
    file_list = os.listdir(os.getcwd())
    for file_name in file_list:
        files = file_name.split(".")
        if files[1] == "pdf":
            rfc_title = str(files[0])
            rfc_id = CalculateHash(rfc_title)
            newLocalRFC = LocalRFCRecord(rfc_id, rfc_title)
            newLRFCdata.append(newLocalRFC.getLocalRFC())
            
    return newLRFCdata


def GetRFC(rfc_id,file_name,peer_ip,peer_port):
    global LRFCdata
    global Server
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(None)
    peer_ipaddr=peer_ip
    s.connect((peer_ipaddr,int(peer_port)))
    
    message = ["GETRFC",str(rfc_id),"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Title: ",file_name,"Client ID: ",str(self_id)]
    s.send(pickle.dumps(message))

    os.chdir(os.getcwd())
    filename=file_name+".pdf"
    file1=open(filename,'wb')
    
    q=s.recv(4096)
    q=pickle.loads(q)
    
    if 'FILE NOT FOUND' in q:
        code = '404'
        phrase = 'FILE NOT FOUND'
        reply = ["P2P-DI/1.0 ",str(code),str(phrase)]
        PrintResponse(reply,'FILERESPN')
    else:
        if 'FILE FOUND' in q:
            last_modified = q[2]
            message = ["OK"]
            s.send(pickle.dumps(message))
            while True:
                q=s.recv(4096)
                if q:
                    file1.write(q)
                else:
                    code = '200'
                    phrase = 'OK'
                    mime = MimeTypes()
                    filesize = os.stat(filename).st_size
                    mime_type = mime.guess_type(filename)
                    reply = ["P2P-DI/1.0 ",str(code),str(phrase),"Last-Modified: ",str(last_modified),"Content-Length: ",str(filesize),"Content-Type: ",str(mime_type[0])]
                    PrintResponse(reply,'FILESENT')
                    file1.close()
                    break

            serverIP = Server[0]
            serverPort = Server[1]
            message=["PQUERY","P2P-DI/1.0 ",str(self_id),"Host: ",IP,"Port: ",str(PORT)]
            reply = client(message,serverIP,serverPort)
            PrintResponse(reply,'PQUERY')
            

            LocalRFC = LocalRFCRecord(rfc_id,file_name)
            LRFCdata.append(LocalRFC.getLocalRFC())
            Local_linked_list.append(LocalRFC.getLocalRFC())

            active_list = reply[4]    
            active_list=RFCStore(active_list,[[rfc_id,file_name]])
    
    s.close()



def SendRFC(rfcid,name, sock):
    global LRFCdata

    file_found = 0

    file_list = os.listdir(os.getcwd())
    for file_name in file_list:
        files = file_name.split(".")
        if files[0] == str(name):
            file_found = 1
            file_name = files[0]
            break

    file_name = file_name+".pdf"
    
    if file_found==0:
        file_data=["P2P-DI/1.0 404","FILE NOT FOUND"]
        sock.send(pickle.dumps(file_data))
    else:
        last_modified = time.strftime("%a, %d %b %Y %X %Z",time.localtime(os.stat(file_name).st_mtime))
        file_data=["P2P-DI/1.0 200","FILE FOUND",str(last_modified)]
        sock.send(pickle.dumps(file_data))
        sock.recv(4096)
        
        with open(file_name,'rb') as f:
            bytesToSend = f.read(4096)
            sock.send(bytesToSend)
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)

    sock.close()



def UpdateDHT(rfcid,rfctitle,peeriip,peerport):
    global self_id
    global linked_list

    data = RFCRecord(rfcid,rfctitle,peeriip,peerport)
    data1 = data.getrfc_record()
    linked_list.append(data1)
    code = '200'
    phrase = 'OK'

    return code, phrase
    

def LookupDHT(rfcid):
    data = linked_list.findNode(rfcid)

    if (data != None):
        code = '200'
        phrase = 'OK'
    else:
        code = '501'
        phrase = 'File not found in database'

    return data, code, phrase
        

def HandleRequest(data,clientsocket,clientaddr):
    global self_id
    global Predecessor
    global PPredecessor
    global Successor
    global TTL
    global BackupRFCdata
    global linked_list
    global bkp_linked_list

    PrintRequest(data)
    rlist = data
    response = ''
    
    if rlist[0] == 'JOIN':
        TTL = 200
        peer_id = rlist[7]
        flag = rlist[9]
        if int(flag) == 0:
            Successor = [rlist[7],rlist[3],rlist[5]]
            Predecessor = [rlist[7],rlist[3],rlist[5]]
            
            Print(['Successor: ',Successor])
            Print(['Predecessor: ',Predecessor])

            response = 'I am your predecessor and successor.'
            clientsocket.send(pickle.dumps(response))
            clientsocket.close()
        else:
            active_list = rlist[11]
            active_peer_ids = [int(x[0]) for x in active_list]
            my_id=int(self_id)
            
            if my_id == max(x for x in active_peer_ids):
                succ_id = min(x for x in active_peer_ids)
                pred_id = max(x for x in active_peer_ids if x < my_id)
            
            elif my_id == min(x for x in active_peer_ids):
                succ_id = min(x for x in active_peer_ids if x > my_id)
                pred_id = max(x for x in active_peer_ids)

            else:
                succ_id = min(x for x in active_peer_ids if x > my_id)
                pred_id = max(x for x in active_peer_ids if x < my_id)

            p = [((y[1]), int(y[2])) for y in active_list if int(y[0]) == pred_id]
            s = [((y[1]), int(y[2])) for y in active_list if int(y[0]) == succ_id]
            c = p[0]
            d = s[0]
            succip = d[0]
            succport = d[1]
            predip = c[0]
            predport = c[1]
            
            Successor = [succ_id, succip,int(succport)]
            Predecessor = [pred_id, predip,int(predport)]

            response='You have joined the Torrent.'
            clientsocket.send(pickle.dumps(response))
            clientsocket.close()
            
    
    elif rlist[0] == 'RFCSTORE':
        data = linked_list.findData(rlist[1])
        
        if (data):
            response =('Data already present in DHT.')
            clientsocket.send(pickle.dumps(response))
            clientsocket.close()
        else:
            file1=rlist[1]
            code,phrase=UpdateDHT(file1[0],file1[1],file1[2],file1[3])

            if str(code) == '200':
                response = ["P2P-DI/1.0 ",str(code),str(phrase),'RFC ',file1[0],file1[1],"New data updated successfully."]
                clientsocket.send(pickle.dumps(response))
                clientsocket.close()
                Print(linked_list.printList(DHTheader))

                succ_msg =["RFCBKP",file1,"P2P-DI/1.0 ","Host: ",IP,"Port: ",str(PORT),"Title: ",file1[1],"Client ID :",str(self_id)]
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                reply = Succs(succ_msg,Succ_IP,Succ_Port)
                if 'Data already present in DHT.' in str(reply):
                    PrintResponse(reply,'RFCBKPA')
                if 'Back up data updated successfully.' in str(reply):
                    PrintResponse(reply,'RFCBKPU')
       
            else:
                response=["P2P-DI/1.0 ",str(code),str(phrase),"Update not successful."]
                clientsocket.send(pickle.dumps(response))
                clientsocket.close()
         
    elif rlist[0] == 'RFCBKP':

        data = bkp_linked_list.findData(rlist[1])
        if (data):
            response =('Data already present in DHT.')
            clientsocket.send(pickle.dumps(response))
            clientsocket.close()
        else:
            bkpdata=rlist[1]
            BackupRFCdata.append(bkpdata)
            bkp_linked_list.append(bkpdata)

            code = '200'
            phrase = 'OK'
            response = ["P2P-DI/1.0 ",str(code),str(phrase),'RFC ',rlist[1],rlist[8],"Back up data updated successfully."]
            clientsocket.send(pickle.dumps(response))
            clientsocket.close()
            
    elif rlist[0] == 'RFCQUERY':
        IP_PORT=IP+':'+str(PORT)
        rIP_PORT = rlist[8]+":"+str(rlist[10])
        if (rIP_PORT != IP_PORT):
            reply,code,phrase=LookupDHT(rlist[1])
            
            if str(code) == '200':

                response ='File data found. Sending the owner the RFC location.'
                clientsocket.send(pickle.dumps(response))
                clientsocket.close()
                
                message=["RFCRESP","P2P-DI/1.0 ",str(code),str(phrase),str(reply[0]),str(reply[1]),str(reply[2]),str(reply[3]),"Host: ",IP,"Port: ",str(PORT),"Client ID: ",str(self_id)]
                peer_ipaddr=rlist[8]
                peer_port=rlist[10]
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.settimeout(None)
                    s.connect((peer_ipaddr,int(peer_port)))
                    s.send(pickle.dumps(message))
                    s.close()
                except:
                    s.close()        
            else:
                response=["P2P-DI/1.0 ",str(code),str(phrase),"No matching id found in database. Forwarding the request."]
                clientsocket.send(pickle.dumps(response))
                clientsocket.close()
                
                message=["RFCQUERY",str(rlist[1]),"P2P-DI/1.0","Host: ",IP,"Title: ",rlist[6],"OrigIP: ",rlist[8],"OrigPort: ",rlist[10],"Client ID: ",str(self_id),"PORT: ",str(PORT)]
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                reply=Succs(message,Succ_IP,Succ_Port)
                
                if 'File data found. Sending the owner the RFC location.' in str(reply):
                    PrintResponse(reply,'RFCQUERYT')
                if 'No matching id found in database. Forwarding the request.' in str(reply):
                    PrintResponse(reply,'RFCQUERYF')

        else:
            code = 601
            response=["P2P-DI/1.0 ",str(code),"I am the originator of this request. No matching peer id found."]
            Print( response)

    elif rlist[0] == 'RFCRESP':
        GetRFC(rlist[4],rlist[5],rlist[6],rlist[7])

    elif rlist[0] == 'GETRFC':
        SendRFC(rlist[1],rlist[8],clientsocket)
            
    elif rlist[0] == 'KEEPALIVE':
        Print(TTL)
        TTL = 200

        Print('Received KP from peer.')

        PPredecessor = rlist[2]
        
    elif rlist[0] == 'MARKSUCC':
        TTL = 200
        Successor = rlist[1]
        message = "P2P-DI/1.0 200 Changed my successor.\n"
        clientsocket.send(pickle.dumps(message))
        clientsocket.close()

    elif rlist[0] == 'LEAVE':
        Predecessor = rlist[2]
        PPredecessor = ''
        message = "P2P-DI/1.0 200 Changed my predecessor.\n"
        clientsocket.send(pickle.dumps(message))
        clientsocket.close()

        message = ["MARKSUCC",[self_id,IP,PORT],"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",str(self_id)]
        Pred_IP = Predecessor[1]
        Pred_Port = Predecessor[2]
        reply = client(message,Pred_IP,Pred_Port)
        PrintResponse(reply,'MARKSUCC')

        for a in range(len(BackupRFCdata)):
            linked_list.append(BackupRFCdata[a])

        bkp_linked_list = LinkedList()
        BackupRFCdata = []

        status = True
        while (status is True):
            status = linked_list.remove(rlist[5],rlist[7])
        Print('Printing udpdated DHT.')
        linked_list.printList(DHTheader)

        message = ["REMOVE",rlist[5],rlist[7],"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"OrigIP: ",IP,"OrigPort: ",PORT,"Client ID: ",str(self_id)]
        Succ_IP = Successor[1]
        Succ_Port = Successor[2]
        reply=Succs(message,Succ_IP,Succ_Port)
        
        if 'Data removed from torrent.' in str(reply):
                    PrintResponse(reply,'REMOVET')
        if 'Removed from my DHT' in str(reply):
                    PrintResponse(reply,'REMOVEC')
        

    elif rlist[0] == 'REMOVE':
        IP_PORT=IP+':'+str(PORT)
        rIP_PORT = rlist[9]+":"+str(rlist[11])
        
        if (rIP_PORT == IP_PORT):
            status = True
            while (status is True):
                status = linked_list.remove(rlist[1],rlist[2])
            linked_list.printList(DHTheader)

            status = True
            while (status is True):
                status = bkp_linked_list.remove(rlist[1],rlist[2])
            bkp_linked_list.printList(DHTheader)
            
            message='Data removed from torrent.'
            clientsocket.send(pickle.dumps(message))
            clientsocket.close()
        else:
            
            status = True
            while (status is True):
                status = linked_list.remove(rlist[1],rlist[2])
            linked_list.printList(DHTheader)

            status = True
            while (status is True):
                status = bkp_linked_list.remove(rlist[1],rlist[2])
            bkp_linked_list.printList(DHTheader)    
            
            message='Removed from my DHT'
            clientsocket.send(pickle.dumps(message))
            clientsocket.close()

            message = ["REMOVE",rlist[1],rlist[2],"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"OrigIP: ",rlist[9],"OrigPort: ",rlist[11],"Client ID: ",str(self_id)]
            Succ_IP = Successor[1]
            Succ_Port = Successor[2]
            reply=Succs(data,Succ_IP,Succ_Port)

            if 'Data removed from torrent.' in str(reply):
                    PrintResponse(reply,'REMOVET')
            if 'Removed from my DHT' in str(reply):
                    PrintResponse(reply,'REMOVEC')

    elif rlist[0] == 'FILTER':
        IP_PORT=IP+':'+str(PORT)
        rIP_PORT = rlist[8]+":"+str(rlist[10])
        
        if (rIP_PORT != IP_PORT):
            filterdata=rlist[1]
            
            for i in range(len(filterdata)):
                data=filterdata[i]
                linked_list.append(data)
                
            message='Added the data to my DHT again.'
            clientsocket.send(pickle.dumps(message))
            clientsocket.close()
        else:
            my_id=int(self_id)
            pred_id=int(Predecessor[0])
            succ_id=int(Succcessor[0])
            filterdata=rlist[1]
            
            for i in range(len(filterdata)):
                data=filterdata[i]
                if my_id < pred_id:
                    
                    if (my_id <= int(data[0]) and succ_id < int(data[0])) or (my_id >= int(data[0]) and succ_id > int(data[0])):
                        data_present = linked_list.findData(data)

                        if (not data_present):
                            linked_list.append(data)
                            filterdata.remove(data)
                else:
                    if my_id >= int(data[0]) and succ_id < int(data[0]):
                        data_present = linked_list.findData(data)

                        if (not data_present):
                            linked_list.append(data)
                            filterdata.remove(data)

            message='Updated my DHT for filtered data.'
            clientsocket.send(pickle.dumps(message))
            clientsocket.close()

            if(filterdata):
                message = ["FILTER",filterdata,"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"OrigIP: ",rlist[8],"OrigPort: ",rlist[10],"Client ID: ",str(self_id)]
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                reply=Succs(data,Succ_IP,Succ_Port)

                if 'Added the data to my DHT again.' in str(reply):
                    PrintResponse(reply,'FILTERA')
                if 'Updated my DHT for filtered data.' in str(reply):
                    PrintResponse(reply,'FILTERU')

    elif rlist[0] == 'BACKUP':
        bkp_linked_list.Empty()
        BackupRFCdata = rlist[1]
        
        for i in range(len(BackupRFCdata)):
            if (BackupRFCdata[i]):
                bkp_linked_list.append(BackupRFCdata[i])


def Handler(clientsocket, clientaddr):

    data = clientsocket.recv(1024)
    try:
        request = pickle.loads(data)
        cur_thread=threading.current_thread()
        HandleRequest(request,clientsocket,clientaddr)
    except:
        clientsocket.close()

def client_as_server():

    cs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs_ip=IP
    cs_port=PORT
    cs_socket.bind((cs_ip,cs_port))
    
    cs_socket.listen(100)

    cs_thread = threading.current_thread()
    Print( "Client-Server Thread started.\n")
    while(1):

        (peer_socket,peer_addr)=cs_socket.accept()
        Print(["Connected to", peer_addr])

        Handler(peer_socket,peer_addr)
        
    cs_socket.close()

    return


def RFCStore(data,Localdata):
    local_rfc = Localdata
    a=data

    active_peer_ids = [int(x[0]) for x in a]
    Local_File_ids = [int(x[0]) for x in local_rfc]
    
    for n in range(len(local_rfc)):
        d = local_rfc[n]
        
        if int(d[0]) > int(max(x for x in active_peer_ids)):
            min_id = int(min(x for x in active_peer_ids))
            p = [((y[1]), int(y[2])) for y in a if int(y[0]) == min_id]
            q = p[0]
            PeerIP = q[0]
            PeerPort = q[1]

        else:
            b = int(min(x for x in active_peer_ids if int(x) >= int(Local_File_ids[n])))
            c = [((y[1]), int(y[2])) for y in a if int(y[0]) == b]
            q = c[0]
            PeerIP = q[0]
            PeerPort = q[1]
        
        message=["RFCSTORE",[str(d[0]),d[1],IP,PORT],"P2P-DI/1.0 ","Host: ",IP,"Port: ",PORT,"Title: ",d[1],"Client ID: ",str(self_id)]
        
        if (PeerIP == IP) and (PeerPort == PORT):
            code,phrase=UpdateDHT(d[0],d[1],IP,PORT)
        else:
            reply = client(message,PeerIP,PeerPort)
            
            if 'Data already present in DHT.' in str(reply):
                PrintResponse(reply,'RFCSTOREA')
                
            if 'New data updated successfully.' in str(reply):
                PrintResponse(reply,'RFCSTOREU')
                
            if 'Update not successful.' in str(reply):
                PrintResponse(reply,'RFCSTOREN')
            
    return a


def JoinTorrent(data,active_list,self_id):
    index_list = data
    a = active_list
    my_id = int(self_id)
    active_peer_ids = [int(x[0]) for x in a]
    
    if int(my_id) == max(x for x in active_peer_ids):
        succ_id = min(x for x in active_peer_ids)
        pred_id = max(x for x in active_peer_ids if x < my_id)
    
    elif int(my_id) == min(x for x in active_peer_ids):
        succ_id = min(x for x in active_peer_ids if x > my_id)
        pred_id = max(x for x in active_peer_ids)

    else:
        succ_id = min(x for x in active_peer_ids if x > my_id)
        pred_id = max(x for x in active_peer_ids if x < my_id)

    p = [((y[1]), int(y[2])) for y in a if int(y[0]) == pred_id]
    s = [((y[1]), int(y[2])) for y in a if int(y[0]) == succ_id]
    c = p[0]
    d = s[0]
    succip = d[0]
    succport = d[1]
    predip = c[0]
    predport = c[1]
    
    succ = [succ_id, succip,succport]
    pred = [pred_id, predip,predport]
    
    message=["JOIN","P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Self-ID: ",my_id,"Flag: ",1,"ActiveList: ",a]
    reply = client(message,succip,succport)
    PrintResponse(reply,'JOIN')
    
    message=["JOIN","P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Self-ID: ",my_id,"Flag: ",1,"ActiveList: ",a]
    reply = client(message,predip,predport)
    PrintResponse(reply,'JOIN')
    
    return succ, pred


def KeepAlive(Succ,serverIP,serverPort,my_id):
    global Successor
    
    
    while(1):
        if(Predecessor):
            message = ["KEEPALIVE",my_id,Predecessor,"P2P-DI/1.0","Host: ",IP,"Port: ",PORT]
            response = client(message,serverIP,serverPort)
            PrintResponse(response,'KEEPALIVE')
            
            if (Successor):
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(None)
                try:
                    s.connect((Succ_IP,int(Succ_Port)))
                    Print("Connecting to Successor peer")
                    s.send(pickle.dumps(message))
                    s.close()
                except:
                    s.close()
            else:
                Print( 'No Successor data\n')
            
        time.sleep(53)
        

def CheckKeepAlive():
    global TTL
    global Predecessor
    global PPredecessor
    global Successor
    global self_id
    global Server
    global BackupRFCdata
    global bkp_linked_list
    ttl=TTL
        
    while (ttl != 0):
        time.sleep(1)
        TTL -= 1
        ttl = TTL
        
    if (Predecessor):
        if ttl == 0:
            
            message = ["LEAVE",Predecessor,self_id,"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",Predecessor[0]]
            server_IP = Server[0]
            server_Port = Server[1]
            reply = client(message,server_IP,server_Port)
            PrintResponse(reply,'LEAVES')
            
            for a in range(len(BackupRFCdata)):
                linked_list.append(BackupRFCdata[a])


            bkp_linked_list = LinkedList()
            BackupRFCdata = []
            
            status = True
            while (status is True):
                status = linked_list.remove(Predecessor[1],Predecessor[2])

            linked_list.printList(DHTheader)

            status = True
            while (status is True):
                status = bkp_linked_list.remove(Predecessor[1],Predecessor[2])

            bkp_linked_list.printList(DHTheader) 
            
            message = ["REMOVE",Predecessor[1],Predecessor[2],"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"OrigIP: ",IP,"OrigPort: ",PORT,"Client ID: ",str(self_id)]
            Succ_IP = Successor[1]
            Succ_Port = Successor[2]
            reply=Succs(message,Succ_IP,Succ_Port)

            if 'Data removed from torrent.' in str(reply):
                PrintResponse(reply,'REMOVET')

            if 'Removed from my DHT' in str(reply):
                PrintResponse(reply,'REMOVEC')

            Predecessor = PPredecessor
            PPredecessor = []

            message = ["MARKSUCC",[self_id,IP,PORT],"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",str(self_id)]
            Pred_IP = Predecessor[1]
            Pred_Port = Predecessor[2]
            reply = client(message,Pred_IP,Pred_Port)
            PrintResponse(reply,'MARKSUCC')



def FilterDHT():
    global Predecessor
    global self_id
    global LRFCdata
    global Local_linked_list

    my_id = self_id
    newLRFCdata = []

    while(1):
        if(Predecessor):
            pred_id=Predecessor[0]
            succ_id=Successor[0]

            filterdata=linked_list.Filter(pred_id,succ_id,my_id)

            if(filterdata):
                message = ["FILTER",filterdata,"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"OrigIP: ",IP,"OrigPort: ",PORT,"Client ID: ",str(self_id)]
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                reply=Succs(message,Succ_IP,Succ_Port)
                
                if 'Added the data to my DHT again.' in str(reply):
                    PrintResponse(reply,'FILTERA')
                    
                if 'Updated my DHT for filtered data.' in str(reply):
                    PrintResponse(reply,'FILTERU')
            else:
                Print('DHT is correctly updated')

            linked_list.sort()
            linked_list.Removedups()
            DHTdata=linked_list.DHTdata()

            if (not DHTdata):
                DHTdata = []
            
            message = ["BACKUP",DHTdata,"P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",str(self_id)]
            Succ_IP = Successor[1]
            Succ_Port = Successor[2]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((Succ_IP,int(Succ_Port)))
                s.send(pickle.dumps(message))
                s.close()
            except:
                s.close()

            linked_list.printList(DHTheader)

            tempLRFCdata = new_rfc_add()
            newLRFCdata = [x for x in tempLRFCdata if x not in LRFCdata]

            if (newLRFCdata):

                for i in range(len(newLRFCdata)):
                    LRFCdata.append(newLRFCdata[i])
                    Local_linked_list.append(newLRFCdata[i])

                serverIP = Server[0]
                serverPort = Server[1]
                message=["PQUERY","P2P-DI/1.0 ",str(self_id),"Host: ",IP,"Port: ",str(PORT)]
                reply = client(message,serverIP,serverPort)
                PrintResponse(reply,'PQUERY')

                active_list = reply[4]
                active_list=RFCStore(active_list,newLRFCdata)
            
        else:
            print 'no pred'

        
        time.sleep(50)
  

def CalculateHash(hashdata):
    md5 = hashlib.md5()
    md5.update(hashdata)
    digest = md5.hexdigest()
    hash_val = int(digest, 16)
    hash_value = str(hash_val)
    
    return hash_value[:3]

def option_list():
    global Successor
    global Predecessor
    global self_id
    global LRFCdata
    global TTL
    global Server
    global rfc_file
    global choice
    global linked_list
    global bkp_linked_list
    
    choice = 0
    TTL = 200
    temp_rfc=list()
    temp_title=list()
    
    Print( "Enter Host name of the Registration Server")
    serverIP=raw_input()
    #serverIP = '192.168.1.110'
    #serverIP = '10.139.67.84'
    #Print( serverIP)
    
    Print( "Enter Port number of the Registration Server")
    serverPort=int(raw_input())
    Server = [serverIP,serverPort]
    
    message=["REGISTER","P2P-DI/1.0","Host: ",IP,"Port: ",str(PORT)]
    reply = client(message,serverIP,serverPort)
    PrintResponse(reply,'REGISTER')
    
    self_id = reply[4]
    
    LRFCdata = initial_rfc_add()
    Local_linked_list.printList(localheader)
    
    thread_fifth=threading.Thread(target=CheckKeepAlive)
    thread_fifth.daemon=True
    thread_fifth.start()
    
    message=["PQUERY","P2P-DI/1.0 ",str(self_id),"Host: ",IP,"Port: ",str(PORT)]
    reply = client(message,serverIP,serverPort)
    PrintResponse(reply,'PQUERY')

    active_list = reply[4]
    
    if len(active_list) == 1:
    
        for n in range(len(LRFCdata)):
            filedata = LRFCdata[n]
            fileid = filedata[0]
            filetitle = filedata[1]

            code,phrase = UpdateDHT(fileid,filetitle,IP,PORT)
            
        linked_list.printList(DHTheader)
        
    elif len(active_list) == 2:
        
        active_peer_ids = [int(x[0]) for x in active_list]
        
        for m in range(len(active_peer_ids)):
            if int(self_id) != int(active_peer_ids[m]):
                peer = active_list[m]
                peerid = peer[0]
                peerIP = peer[1]
                peerPort = int(peer[2])

                message=["JOIN","P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Self-ID: ",self_id,"Flag: ",0,"ActiveList: ",active_list]
                reply = client(message,peerIP,peerPort)
                PrintResponse(reply,'JOIN')

                Successor = [peerid,peerIP,peerPort]
                Predecessor = [peerid,peerIP,peerPort]

                active_list=RFCStore(active_list,LRFCdata)
                    
    elif len(active_list) > 2:
        P_Succ, P_Pred = JoinTorrent(reply,active_list,self_id)
        active_list=RFCStore(active_list,LRFCdata)
        
        SuccIP = P_Succ[1]
        SuccPort = P_Succ[2]
        Successor = P_Succ
        
        PredIP = P_Pred[1]
        PredPort = P_Pred[2]
        Predecessor = P_Pred

    else:
        Print('Invalid Index List')

    thread_fourth=threading.Thread(target=KeepAlive,args=(Successor,serverIP,serverPort,self_id))
    thread_fourth.daemon=True
    thread_fourth.start()

    thread_seven=threading.Thread(target=FilterDHT)
    thread_seven.daemon=True
    thread_seven.start()

        
    while(1):

        if choice==1:
            Print('********************************************************************')
            Print('Printing DHT ')
            linked_list.printList(DHTheader)
            Print(' ')
            Print('Printing BackupDHT ')
            bkp_linked_list.printList(DHTheader)
            Print('********************************************************************')
            choice = ''

        if choice==2:

            message=["PQUERY","P2P-DI/1.0 ",str(self_id),"Host: ",IP,"Port: ",str(PORT)]
            reply = client(message,serverIP,serverPort)
            indexlist = reply[4]
            indexlist=tabulate(indexlist, headers=['Client ID', 'Host IP','Host Port','Status','Time-to-Live'],tablefmt='grid')
            Print('********************************************************************')
            Print('Printing Index List of Active Peers: ')
            Print(indexlist)
            Print('********************************************************************')
            
            choice = ''

        elif choice==3:

            rfc_title=rfc_file
            x = rfc_file
            rfc_id=CalculateHash(x)
            reply,code,phrase=LookupDHT(rfc_id)
            
            if str(code) == '200':
                GetRFC(str(reply[0]),str(reply[1]),str(reply[2]),str(reply[3]))
            else:            
                message=["RFCQUERY",str(rfc_id),"P2P-DI/1.0","Host: ",IP,"Title: ",rfc_title,"OrigIP: ",IP,"OrigPort: ",PORT,"Client ID: ",str(self_id),"PORT: ",str(PORT)]
                Succ_IP = Successor[1]
                Succ_Port = Successor[2]
                reply=Succs(message, Succ_IP, Succ_Port)
                
                if 'File data found. Sending the owner the RFC location.' in str(reply):
                    PrintResponse(reply,'RFCQUERYT')
                    
                if 'No matching id found in database. Forwarding the request.' in str(reply):
                    PrintResponse(reply,'RFCQUERYF')

            choice = ''
            
        elif choice==4:
            Print('********************************************************************')
            Print('My Successor: '+str(Successor))
            Print('My Predecessor: '+str(Predecessor))
            Print('********************************************************************')
            
            choice = ''

        elif choice==5:
            
            message=["LEAVE",[self_id,IP,PORT],Predecessor," P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",str(self_id)]
            reply = client(message, serverIP, serverPort)
            
            PrintResponse(reply,'LEAVES')
            
            if (Successor):
                SuccIP = Successor[1]
                SuccPort = Successor[2]
                message=["LEAVE",[self_id,IP,PORT],Predecessor," P2P-DI/1.0","Host: ",IP,"Port: ",PORT,"Client ID: ",str(self_id)]
                response = Succs(message, SuccIP, SuccPort)
                PrintResponse(response,'LEAVEC')

            Successor = []
            Predecessor = []
            choice = ''
            
            break

        time.sleep(1)
    return            


def EvaluateInput():
    global choice
    global rfc_file
    filename='input.txt'
    inlist=[]    
    prevstat=0
    
    with open(filename, "w"):
        pass
    
    while(True):
        currstat=os.stat('input.txt').st_mtime
        inlist=[]
        if (currstat > prevstat):
            try:  
                file1=open(filename,'r')
                for line in file1:
                    line=line.strip('\n')
                    inlist.append(line)
                size=len(inlist)
                       
                data=inlist[(size-1)]
                data=data.split(' ', 1)
                code=data[0]
                if int(code)==3:
                    choice = int(data[0])
                    rfc_file = data[1]
                elif int(code)==1 or int(code)==2 or int(code)==4 or int(code)==5:
                    choice = int(data[0])
                else:
                    response = "P2P-DI/1.0 "+str('400') +" " +str('Bad Request') +"\nClient-ID: " +str(self_id)+"\nResponse: 'Incorrect Request'\nDate: "+datetime
                    Print('********************************************************************')
                    Print(response)
                    Print('********************************************************************')            
        
                    choice = 0
                prevstat = currstat
            except:
                file1.close()
        time.sleep(10)
        file1.close()



def client(message, serverIP, serverPort):
    try:
        serverPort=int(serverPort)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(None)
        sock.connect((serverIP,int(serverPort)))

        sock.send(pickle.dumps(message))
        reply=sock.recv(16384)
        reply = pickle.loads(reply)

        sock.close()
        return reply
    except socket.error as e:
        print e.strerror
        sock.close()
        return None
        sys.exit(0)
        

def Succs(message, SuccIP, SuccPort):
    try:
        SuccPort = int(SuccPort)
        Succsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Succsock.settimeout(None)
        Succsock.connect((SuccIP,SuccPort))

        Succsock.send(pickle.dumps(message))
        reply=Succsock.recv(16384)
        reply = pickle.loads(reply)

        Succsock.close()
        return reply
    except socket.error as e:
        print e.strerror
        Succsock.close()
        return None
        sys.exit(0)

def Peer(message, PeerIP, PeerPort):
    try:
        PeerPort=int(PeerPort)
        peersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peersock.settimeout(None)
        peersock.connect((PeerIP,PeerPort))

        peersock.send(pickle.dumps(message))
        reply=peersock.recv(16384)
        reply = pickle.loads(reply)

        peersock.close()
        return reply
    except socket.error as e:
        print e.strerror
        peersock.close()
        return None
        sys.exit(0)

def Print(data):
    lock.acquire()
    print data
    lock.release()

def PrintRequest(message):
                
        if message[0] == 'JOIN':
                message = "JOIN P2P-DI/1.0 \nClient ID: "+ str(message[7])+" \nHost: "+str(message[3])+"\nPort: "+str(message[5])+"\nOS: "+OS

        if message[0] == 'RFCQUERY':
                message = "RFCQUERY "+str(message[1])+" P2P-DI/1.0 \nRFC Title: "+str(message[6])+" \nClient ID: "+str(message[12])+"\nHost: "+str(message[4])+"\nPORT: "+str(message[14])+"\nOrigin Host: "+str(message[8])+"\nOrigin Port: "+str(message[10])+"\nOS: "+OS
                
        if message[0] == 'RFCRESP':
                message = "RFCRESP P2P-DI/1.0 \nRFC Owner: "+ str(message[6])+ " "+ str(message[7])+"\nClient ID: "+ str(message[13])+" \nHost: "+str(message[9])+"\nPort: "+str(message[11])+"\nOS: "+OS

        if message[0] == 'RFCSTORE':
                file1 = message[1]
                fileid = file1[0]
                filetitle = file1[1]
                message = "RFCSTORE "+str(fileid)+" P2P-DI/1.0 \nRFC Title: "+str(filetitle)+ "\nClient ID: "+ str(message[10])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS

        if message[0] == 'RFCBKP':
                file1 = message[1]
                fileid = file1[0]
                filetitle = file1[1]
                message = "RFCBKP "+str(fileid)+" P2P-DI/1.0 \nRFC Title: "+str(filetitle)+ "\nClient ID: "+ str(message[10])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS

        if message[0] == 'GETRFC':
                message = "GET RFC "+str(message[1])+" P2P-DI/1.0 \nRFC Title: "+str(message[8])+ "\nClient ID: "+ str(message[10])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS
                
        if message[0] == 'KEEPALIVE':
                message = "KEEPALIVE "+str(message[1])+ " " + str(message[2]) +" P2P-DI/1.0 \nClient ID: "+ str(message[1])+" \nHost: "+str(message[5])+"\nPort: "+str(message[7])+"\nOS: "+OS

        if message[0] == 'MARKSUCC':
                message = "MARKSUCC "+str(message[1])+ " P2P-DI/1.0 \nClient ID: "+ str(message[8])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS

        if message[0] == 'LEAVE':
                message = "LEAVE "+str(message[1])+ " " + str(message[2]) +" P2P-DI/1.0 \nClient ID: "+ str(message[9])+" \nHost: "+str(message[5])+"\nPort: "+str(message[7])+"\nOS: "+OS

        if message[0] == 'REMOVE':
                message = "REMOVE "+str(message[1])+ " " + str(message[2]) +" P2P-DI/1.0 \nClient ID: "+ str(message[13])+" \nHost: "+str(message[5])+"\nPort: "+str(message[7])+"\nOrigin Host: "+str(message[9])+"\nOrigin Port: "+str(message[11])+"\nOS: "+OS

        if message[0] == 'FILTER':
                filterdata=tabulate(message[1], headers=DHTheader,tablefmt='grid')
                message = "FILTER P2P-DI/1.0 \nClient ID: "+ str(message[12])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOrigin Host: "+str(message[8])+"\nOrigin Port: "+str(message[10])+"\nOS: "+OS+"\nFiltered Data: \n"+filterdata

        if message[0] == 'BACKUP':
                backup=tabulate(message[1], headers=DHTheader,tablefmt='grid')
                message = "BACKUP P2P-DI/1.0 \nClient ID: "+ str(message[8])+" \nHost: "+str(message[4])+"\nPort: "+str(message[6])+"\nOS: "+OS+"\nBackup Data: \n"+backup

        Print('********************************************************')
        Print(message )
        Print('********************************************************')


def PrintResponse(response,request):
                                                                                                                                                     
    if request == 'REGISTER':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nClient-ID: " +str(response[4])+"\nResponse: 'You have registered successfully'\nDate: "+datetime

    if request == 'PQUERY':
        indexlist=tabulate(response[4], headers=['Client ID', 'Host IP','Host Port','Status','Time-to-Live'],tablefmt='grid')
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Index list sent successfully'\nDate: "+datetime+"\nIndex List:\n " +indexlist

    if request == 'JOIN':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'You have joined torrent successfully'\nDate: "+datetime

    if request == 'RFCQUERYF':
        response = "P2P-DI/1.0 "+str('181') +" " +str('Forwarding the request') +"\nResponse: 'File data not found in database. Forwarding the request.'\nDate: "+datetime

    if request == 'RFCQUERYT':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'File data found in database. Sending client the RFC location.'\nDate: "+datetime

    if request == 'RFCSTOREU':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Updated my database successfully.'\nDate: "+datetime

    if request == 'RFCSTOREN':
        response = "P2P-DI/1.0 "+str('500') +" " +str('Internal Server Error') +"\nResponse: 'Update not successful.'\nDate: "+datetime

    if request == 'RFCSTOREA':
        response = "P2P-DI/1.0 "+str('100') +" " +str('Already Present') +"\nResponse: 'File data already present in database.'\nDate: "+datetime

    if request == 'RFCBKPU':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Back up data updated successfully.'\nDate: "+datetime

    if request == 'RFCBKPA':
        response = "P2P-DI/1.0 "+str('100') +" " +str('Already Presen') +"\nResponse: 'Back up data already present in database.'\nDate: "+datetime

    if request == 'KEEPALIVE':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Keep Alive acknowledged by Server.'\nDate: "+datetime

    if request == 'MARKSUCC':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Successor updated successfully.'\nDate: "+datetime

    if request == 'LEAVES':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Flag set to inactive. Thank You!'\nDate: "+datetime

    if request == 'LEAVEC':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Updated my predecessor successfully'\nDate: "+datetime

    if request == 'REMOVEC':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Data removed from my database successfully.'\nDate: "+datetime

    if request == 'REMOVET':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Data removed from torrent successfully.'\nDate: "+datetime

    if request == 'FILTERU':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'Updated my database for filtered data received.'\nDate: "+datetime

    if request == 'FILTERA':
        response = "P2P-DI/1.0 "+str('202') +" " +str('OK') +"\nResponse: 'Added file data to my database again.'\nDate: "+datetime

    if request == 'FILERESPN':
        response = "P2P-DI/1.0 "+str('404') +" " +str('File Not Found') +"\nResponse: 'File is not present with me.'\nDate: "+datetime

    if request == 'FILESENT':
        response = "P2P-DI/1.0 "+str('200') +" " +str('OK') +"\nResponse: 'File sent successfully.'\nDate: "+datetime+"\nLast-Modified: "+str(response[4])+"\nContent-Length: "+str(response[6])+"\nContent-Type: "+str(response[8])
        
    Print('********************************************************')
    Print( response)
    Print('********************************************************')


def main():

    global PORT
    global IP
    global linked_list
    global Local_linked_list
    global bkp_linked_list
    global TTL
    
    TTL = 200
    linked_list = LinkedList()
    Local_linked_list = LinkedList()
    bkp_linked_list = LinkedList()

    print "Enter IP address of the host: "
    IP=raw_input()
    #IP = '192.168.1.110'
    #IP = '10.139.67.84'
    #Print( IP)
    Print( "Enter Upload Port number: ")
    PORT=int(raw_input())
    
    try:
        thread_first = threading.Thread(target=client_as_server)
        thread_second = threading.Thread(target=option_list)
        thread_third=threading.Thread(target=EvaluateInput)
        
        thread_first.daemon=True
        thread_second.daemon=True
        thread_third.daemon=True
    
        thread_first.start()
        thread_second.start()
        thread_third.start()

        thread_first.join()
        thread_second.join()
        thread_third.join()

    except KeyboardInterrupt:
        sys.exit(0)


if __name__=="__main__":
    main()
