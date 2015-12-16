print'IP'

while(1):
    print "Select an option from below"
    print "1. Print my Distributed Hash Table"
    print "2. Print list of Active Peers in Torrent"
    print "3. Look for a new RFC"
    print "4. Print my Neighbour peers"
    print "5. Leave"

    filename="input.txt"
    file1=open(filename,'a')
    
    choice=int(raw_input())
    
    if choice==3:
      print( "Enter the RFC title")
      rfc_title=raw_input()
      data = str(choice)+" "+rfc_title
    else:
      data = str(choice)

    print data
    
    file1.write(data)
    file1.write('\n')
    file1.close()

        
