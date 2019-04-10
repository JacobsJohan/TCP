import SharedFunctions as sf
import fileMgmt as music
import threading
import os
import time

GNUThread = threading.Event()


# Run the GRC flowgraph which updates the angle in a file
def runGNURadio():
    print("Running gnu radio")
    music.main()

# Read out the file that contains a single line with (AoA, timestamp)
def readFile(filename):
    AoA = "(0, 0)"
    with open(filename, 'r') as f:
        for line in f:
            AoA = line
            break
    return AoA

def main():
    print("Starting up client")

    # Create a client socket at the same IP and port as receiver in order to send to the server
    #serverIP = '192.168.0.128'
    serverIP = '192.168.192.1'
    serverPort = 5000

    filename = os.getcwd()
    filename += '/angle.txt'

    running = True
    while running:
        # Open a socket to connect with server
        s = sf.createSocket(serverIP, serverPort, serverBool=False)

        # After connection is established, wait for input from Server
        task = s.recv(1024)
        print("New task is: ", task)
        if (task == b'GRC'):
            if not(GNUThread.is_set()):
                threading.Thread(target = music.main).start()
                GNUThread.set()
        elif (task == b'AoA'):
            AoA = readFile(filename)
            #s.sendall(AoA.to_bytes(1, byteorder='big'))
            s.sendall(AoA.encode('utf-8'))
        elif (task == b'Shut down'):
            running = False
            music.exitThread.set()
        else:
            print("Got unknown command: ", task)
        s.close()
    #clientSock.close() #not needed apparently



if __name__ == '__main__':
    main()

