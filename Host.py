#! /usr/bin/python3
import SharedFunctions as sf
import socket
import platform
import threading
import time
import keyboard

ipList = []
radioList = []
running = True

class Radio:
    def __init__(self, ip):
        print("Creating radio")
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

# DEPRECATED
def commandBasedConn():
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
    #serverIP = '192.168.0.128'
    serverIP = '192.168.0.250'
    serverPort = 5000

    s = sf.createSocket(serverIP, serverPort, serverBool=True)

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
            # GRC: tell client to run GNU radio flowgraph
            if (command == 'GRC'):
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
    

# Setup a connection with a client. Tell client to start measuring AoA and then periodically request this angle.
def setupConnection(ip, port):
    # Create a server socket at desired port
    s = sf.createSocket(ip, port, serverBool=True)

    # Listen on port for incoming connections
    s.listen(1)
    conn, addr = s.accept()
    print("Connection from:" + str(addr))

    # Tell client to run GRC
    command = 'GRC'
    conn.sendall(command.encode('utf-8'))

    # Wait 10s to ensure everything is up and running
    time.sleep(2)
    
    # Get current radio object
    radio = getRadio(addr[0])

    # Now that everything is up and running, continuously ask for the AoA
    while running:
        s.listen(1)                             # The 1 specifies the backlog parameter which is the amount of allowed connections
        conn, addr = s.accept()                 # conn = a new socket to send/rcv data; addr = the address on the other end

        command = 'AoA'
        conn.sendall(command.encode('utf-8'))
        aoa_b = conn.recv(1024)
        #radio.aoa = int.from_bytes(aoa_b, byteorder='big')
        radio.aoa = float(aoa_b.decode('utf-8'))

        print("AoA is: ", radio.aoa)
        time.sleep(0.5)
        
    # When running = False, send message to client to shut down
    s.listen(1)
    conn, addr = s.accept()
    command = 'Shut down'
    conn.sendall(command.encode('utf-8'))
    time.sleep(1)
        

def shutdownCheck():
    global running
    while True:
        try:
            if (keyboard.is_pressed('q')):
                print("Quitting")
                running = False
                break
            else:
                pass
        except BaseException as e:
            print(e)
            break


def inputCheck():
    global running
    while True:
        command = str(input("Enter q to quit \n -->"))
        if (command == 'q'):
            running = False
            break
        else:
            pass
    print("Shutting down")
    return 0
    

def main():
    print("Starting up server...")

    serverIP = '192.168.192.1'
    #serverIP = '192.168.0.250'
    serverPort = 5000
    
    # Define the amount of SDRs that will be computing AoAs
    while True:
        try:
            nrOfRadios = int(input("How many radios will be used? \n ->"))
            break
        except BaseException as e:
            print(e)

    # Create 1 thread for each SDR
    for i in range(nrOfRadios):
        serverPort += i
        threading.Thread(target = setupConnection, args = (serverIP, serverPort)).start()

    #print("Press q to quit")
    threading.Thread(target = inputCheck).start()
    


if __name__ == '__main__':
    main()

