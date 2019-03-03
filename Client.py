import SharedFunctions as sf
import threading

GNUThread = threading.Event()
AoA = 90


def runGNURadio():
    print("running gnu radio")
    #AoA should be updated in here somewhere

def main():
    print("Starting up client")

    # Create a client socket at the same IP and port as receiver in order to send to the server
    # serverIP = '127.0.0.1'
    serverIP = '192.168.0.128'
    serverPort = 5000

    running = True
    while running:
        #data = str(input("What is your message? \n--> "))
        #data_b = data.encode('utf-8')
        s = sf.createSocket(serverIP, serverPort, serverBool=False)

        # After connection is established, wait for input from Server
        task = s.recv(1024)
        print("New task is: ", task)
        if (task == b'GNU'):
            if not(GNUThread.is_set()):
                threading.Thread(target = runGNURadio).start()
                GNUThread.set()
        elif (task == b'AoA'):
            s.sendall(AoA.to_bytes(1, byteorder='big'))
        elif (task == b'Shut down'):
            running = False
        else:
            print("Got unknown command: ", task)
    #clientSock.close() #not needed apparently



if __name__ == '__main__':
    main()

