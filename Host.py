#! /usr/bin/python3
import SharedFunctions as sf
import socket
import platform

ipList = []
radioList = []

class Radio:

    def __init__(self, ip):
        self.ip = ip
        self.aoa = 0        # Initial AoA is 0


def getRadio(ip):
    # Start of by checking if the radio exists
    for i in range(len(ipList)):
        if (ip == ipList[i]):
            radio = radioList[i]
            return radio

    # If previous loop does not find the radio, create a new one and return it
    radio = Radio(ip)
    radioList.append(radio)
    return radio




def main():
    print(platform.python_version())
    print("Starting up server")

    # Define the amount of SDRs that will be computing AoAs
    '''
    while True:
        try:
            nrOfRadios = int(input("How many radios will be used? \n ->"))
            break
        except BaseException as e:
            print(e)
    '''

    # Create a server socket at port 5000
    #serverIP = '127.0.0.1'
    #serverIP = '192.168.0.128'
    serverIP = '192.168.0.250'
    serverPort = 5000

    s = sf.createSocket(serverIP, serverPort, serverBool=True)

    running = True

    while running:
        s.listen(1)    # The 1 specifies the backlog parameter which is the amount of allowed connections
        conn, addr = s.accept()    # conn = a new socket to send/rcv data; addr = the address on the other end
        print("Connection from:" + str(addr))

        # Check if ip already known
        radio = getRadio(addr[0])

        #data = int.from_bytes(data, byteorder='big')
        #print("Received data is: ", data)
        if (radio.ip == '192.168.0.170'):
            print("Choose a command from: GNU, AoA, Shut down")
            command = str(input("--> "))
            conn.sendall(command.encode('utf-8'))

            # Based on the given command, a reply is (not) expected
            # GNU: tell client to run GNU radio flowgraph
            if (command == 'GNU'):
                print("No reply expected")
            elif (command == 'AoA'):
                aoa_b = conn.recv(1024)
                aoa = int.from_bytes(aoa_b, byteorder='big')
                print("AoA is: ", aoa)
                # functionSetAoA
            elif (command == 'Shut down'):
                running = False
            else:
                print("Wrong command")

        conn.close()
    s.close()





if __name__ == '__main__':
    main()

