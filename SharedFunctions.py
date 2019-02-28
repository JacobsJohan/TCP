import socket



# Create a socket for either a client or a server. If serverBool is True,
def createSocket(ip, port, serverBool=None):
    if (serverBool is None):
        serverBool = False
    s = socket.socket()

    if serverBool:
        s.bind((ip, port))
    else:
        s.connect((ip, port))
    return s

def rcvAll(c):
    data = c.recv(1024)
    maxlen = 255 # We can only send 256 dwords, but header up to message length already contains a dword
    msglen_b = data[2].to_bytes(1, byteorder='big') + data[3].to_bytes(1, byteorder='big')
    msglen = int.from_bytes(msglen_b, byteorder='big')
    while (msglen> maxlen):
        data = data + c.recv(1024)
        msglen = msglen - maxlen
    return data