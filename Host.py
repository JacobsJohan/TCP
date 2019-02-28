import socket
import SharedFunctions as sf



def main():
    print("Starting up server")

    # Create a server socket at port 5000
    #serverIP = '127.0.0.1'
    serverIP = '192.168.0.128'
    serverPort = 5000
    serverSock = sf.createSocket(serverIP, serverPort, serverBool=True)

    running = True

    while running:
        serverSock.listen(1)    # The 1 specifies the backlog parameter which is the amount of allowed connections
        conn, addr = serverSock.accept()    # conn = a new socket to send/rcv data; addr = the address on the other end
        print("Connection from:" + str(addr))
        #data = tl.recvall(c)
        data = conn.recv(1024)

        #data = int.from_bytes(data, byteorder='big')
        print("Received data is: ", data)
        conn.close()
        if (data.decode('utf-8') == 'Shut down'):
            break





if __name__ == '__main__':
    main()

