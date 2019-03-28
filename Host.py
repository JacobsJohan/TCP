import SharedFunctions as sf
import socket
import platform
import threading
import time
import keyboard
import matplotlib.pyplot as plt
import numpy as np
import json

radioList = []
running = True

# Create a radio with an IP-address, x position and y position (location of the
# antenna array)
class Radio:
    def __init__(self, ip, x, y):
        #print("Creating radio")
        self.ip = ip
        self.x = x
        self.y = y
        self.aoa = 0        # Initial AoA is 0

# Function to read config file. On each line of the config file should be a dictionary with the anchor IP, x-position and y-position
def readConfig(filename):
    with open(filename, 'r') as f:
        for line in f:
            dict = json.loads(line)
            radio = Radio(dict['ip'], dict['x'], dict['y'])
            radioList.append(radio)


# Find the connected device by comparing the IP that connected with the known IPs from the radioList
def getRadio(ip):
    # Start of by checking if the radio exists
    for radio in radioList:
        if (ip == radio.ip):
            return radio

    # If previous loop does not find the radio, create a new one and return it
    print("Unknown connection from ", ip)
    return -1


# Setup a connection with a client. Tell client to start measuring AoA and then periodically request this angle.
def setupConnection(ip, port):
    # Create a server socket at desired port
    s = sf.createSocket(ip, port, serverBool=True)

    # Listen on port for incoming connections
    s.listen(1)
    conn, addr = s.accept()
    print("Connection from:" + str(addr))

    # Get current radio object
    radio = getRadio(addr[0])
    if (radio == -1):
        print("Shutting down")
        return -1

    # Tell client to run GRC
    command = 'GRC'
    conn.sendall(command.encode('utf-8'))

    # Wait 10s to ensure everything is up and running
    time.sleep(2)
    

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
        

# Function that checks if q is pressed on the keyboard. If so, it will shut down the system.
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

# Function that checks if q is pressed on the keyboard. If so, it will shut down the system.
def inputCheck():
    global running
    while True:
        command = raw_input("Enter q to quit \n -->")
        #command = str(input("Enter q to quit \n -->"))
        if (command == 'q'):
            running = False
            break
        else:
            pass
    print("Shutting down")
    return 0


# Perform triangulation based on 2 computed angles of arrival   
def triangulate(x1, y1, theta1, x2, y2, theta2, plot=False):
    # Compute line parameters (a, b) from y = ax + b
    a1 = np.tan(theta1)
    b1 = y1 - a1*x1

    a2 = -np.tan(np.pi/2 - theta2)
    b2 = y2 - a2*x2

    # Compute intersect of 2 lines
    x = (b2 - b1)/(a1 - a2)
    y = a1*x + b1 # y = a2*x + b2 (also works)

    # Plot lines and intersect if desired
    if plot:
        X1 = np.linspace(0, 10, 101)
        Y1 = a1*X1 + b1

        X2 = np.linspace(0, 10, 101)
        Y2 = a2*X2 + b2

        plt.plot(X1, Y1, 'b')
        plt.plot(X2, Y2, 'r')
        plt.plot(x, y, '*')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Triangulation')
        plt.grid(True)
        plt.show()

    return (x, y) 

def main():
    print("Starting up server...")

    # Create radioList based on entries in config.txt
    filename = 'config.txt'
    readConfig(filename)

    serverIP = '192.168.192.1'
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
    threading.Thread(target = shutdownCheck).start()


if __name__ == '__main__':
    main()




'''


# DEPRECATED
def commandBasedConn():
    # Define the amount of SDRs that will be computing AoAs
    
    while True:
        try:
            nrOfRadios = int(input("How many radios will be used? \n ->"))
            break
        except BaseException as e:
            print(e)
    

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
'''
