import socket
import SharedFunctions as sf



def main():
    print("Starting up client")

    angle = 123
    angle_b = angle.to_bytes(4, byteorder='big')

    # Create a client socket at the same IP and port as receiver in order to send to the server
    serverIP = '127.0.0.1'
    serverPort = 5000

    data = None
    while (data != 'Shut down'):
        data = str(input("What is your message? \n--> "))
        data_b = data.encode('utf-8')
        clientSock = sf.createSocket(serverIP, serverPort, serverBool=False)
        clientSock.sendall(data_b)

    #clientSock.close() #not needed apparently



if __name__ == '__main__':
    main()

