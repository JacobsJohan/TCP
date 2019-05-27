import socket

# Create a socket for either a client or a server.
def createSocket(ip, port, serverBool=None):
    if (serverBool is None):
        serverBool = False
    s = socket.socket()

    if serverBool:
        s.bind((ip, port))
    else:
        s.connect((ip, port))
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s
