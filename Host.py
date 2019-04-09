import SharedFunctions as sf
import socket
import platform
import threading
import time
import keyboard
import matplotlib.pyplot as plt
import numpy as np
import json
from tkinter import *
import random

radioList = []
state = 'ini'     # Can be 'run', 'pause' or 'quit' (or 'ini' for initial state)
xpos = 0
ypos = 0

# GUI dimensions
WIDTH = 720
HEIGHT = 480

# Create a radio with an IP-address, x position and y position (location of the
# antenna array)
class Radio:
    def __init__(self, ip, x, y, orientation):
        #print("Creating radio")
        self.ip = ip
        self.x = x
        self.y = y
        self.aoa = 0                    # Initial AoA is 0
        self.orientation = orientation  # Relative orientation for triangulation

# Function to read config file. On each line of the config file should be a dictionary with the anchor IP, x-position and y-position
def readConfig(filename):
    with open(filename, 'r') as f:
        for line in f:
            dict = json.loads(line)
            radio = Radio(dict['ip'], dict['x'], dict['y'], dict['orientation'])
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
    while (state != 'quit'):
        s.listen(1)                             # The 1 specifies the backlog parameter which is the amount of allowed connections
        conn, addr = s.accept()                 # conn = a new socket to send/rcv data; addr = the address on the other end

        if (state == 'run'):
            command = 'AoA'
            conn.sendall(command.encode('utf-8'))
            aoa_b = conn.recv(1024)
            radio.aoa = float(aoa_b.decode('utf-8'))
        else:
            # System is paused, so keep checking if it is unpaused
            while True:
                if (state == 'run'):
                    command = 'AoA'
                    conn.sendall(command.encode('utf-8'))
                    aoa_b = conn.recv(1024)
                    radio.aoa = float(aoa_b.decode('utf-8'))
                elif (state == 'quit'):
                    break
                else:
                    time.sleep(0.5)
        #print("AoA is: ", radio.aoa)
        time.sleep(0.5)
        
    # When running = False, send message to client to shut down
    s.listen(1)
    conn, addr = s.accept()
    command = 'Shut down'
    conn.sendall(command.encode('utf-8'))
    time.sleep(1)
        

# Function that checks if q is pressed on the keyboard. If so, it will shut down the system. Requires sudo access.
# NO LONGER NEEDED IF GUI STOP BUTTON IS IMPLEMENTED
def shutdownCheck():
    global state
    while True:
        try:
            if (keyboard.is_pressed('q')):
                print("Quitting")
                state = 'quit'
                break
            else:
                pass
        except BaseException as e:
            print(e)
            break

# Function that checks if q is pressed on the keyboard. If so, it will shut down the system.
# NO LONGER NEEDED IF GUI STOP BUTTON IS IMPLEMENTED
def inputCheck():
    global state
    while True:
        command = raw_input("Enter q to quit \n -->")
        #command = str(input("Enter q to quit \n -->"))
        if (command == 'q'):
            state = 'quit'
            break
        else:
            pass
    print("Shutting down")
    return 0


# Perform triangulation based on 2 computed angles of arrival   
def triangulate(x1, y1, theta1, x2, y2, theta2, plot=False):
    # Compute line parameters (a, b) from y = ax + b
    theta1 = theta1/180*np.pi
    theta2 = theta2/180*np.pi

    a1 = np.tan(theta1)
    b1 = y1 - a1*x1

    theta2_ = theta2 - np.pi/2
    a2 = np.tan(theta2_)
    b2 = y2 - a2*x2

    # Compute intersect of 2 lines
    x = (b2 - b1)/(a1 - a2)
    y = a1*x + b1 # y = a2*x + b2 (also works)

    #print("a1:",a1)
    #print("a2:",a2)

    # Plot lines and intersect if desired
    if plot:
        X1 = np.linspace(0, 200, 2001)
        Y1 = a1*X1 + b1

        X2 = np.linspace(0, 200, 2001)
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

# Takes tuples of 4 arguments as input (xpos, ypos, angle, orientation) and performs triangulation based on that
# by taking the average over the n computed positions
def triangulate_n():
    narg = len(radioList)
    if (narg < 2):
        print("Need at least 2 antenna arrays for triangulation")
        return

    A = [0]*narg
    B = [0]*narg
    X = [0]*(narg-1)
    Y = [0]*(narg-1)
    for i in range(narg):
        # Note: these local variables are only defined to improve readability
        x_rig = radioList[i].x
        y_rig = radioList[i].y
        theta = radioList[i].aoa / 180 * np.pi
        orientation = radioList[i].orientation
        
        # Check if the angle needs to be adjusted based on the position of the antenna array
        if (orientation == 1):
            #theta = np.pi - theta
            theta = theta - np.pi/2
        elif (orientation == 2):
            theta = np.pi + theta
        elif (orientation == 3):
            theta = 3.0/2.0*np.pi + theta
        else:
            pass

        # Slope & intersection
        A[i] = np.tan(theta)
        B[i] = y_rig - A[i]*x_rig

    # Compute intersection of 2 lines with equation y = a*x + b
    for i in range(narg-1):
        X[i] = (B[i+1] - B[0]) / (A[0] - A[i+1])
        Y[i] = A[i]*X[i] + B[i]
        
    # Now we have the position computed based on narg lines. Take the average of all results to find final result
    x = 0
    y = 0
    n = 0
    for i in range(narg-1):
        # Make sure that a and b are not equal to inf. Else this could have given a division by 0 in the previous step
        if (np.abs(A[i]) < 1e6 and np.abs(B[i]) < 1e6):
            x = x + X[i]
            y = y + Y[i]
            n = n + 1
        else:
            pass
    x = x/n
    y = y/n
    return (x, y)

# Kalman filter for a system without known input
def KalmanFilter(x_prev, P_prev, y, F, H, Q, R):
    # Prediction step
    x_hat = np.matmul(F, x_prev)
    P_hat = np.matmul(np.matmul(F, P_prev), F.T) + Q

    # Innovation step
    S = np.matmul(np.matmul(H, P_hat), H.T) + R
    K = np.matmul(np.matmul(P_hat, H.T), np.linalg.inv(S))
    P_new = np.matmul((np.identity(K.shape[0]) - np.matmul(K, H)), P_hat)
    y_tilde = y - np.matmul(H, x_hat)
    x_new = x_hat + np.matmul(K, y_tilde)
    # delta = np.abs(x_prev[2,1] - x_new[2,1])
    return (x_new, P_new)
    
        

F = np.identity(2)
H = np.identity(2)
P_prev = np.identity(2)
x_prev = np.array((0, 0))
R = np.identity(2)
Q = np.identity(2)*0.1

# Continuosly compute the position of the transmitter, unless the system is paused.
def computePosition():
    global xpos, ypos, x_prev, P_prev

    # Continuously perform triangulation
    while True:
        if (state == 'run'):
            '''
            (xpos, ypos) = triangulate(radioList[0].x,
                                       radioList[0].y,
                                       radioList[0].aoa,
                                       radioList[1].x,
                                       radioList[1].y,
                                       radioList[1].aoa,
                                       plot=False)
            '''
            (xpos, ypos) = triangulate_n()

            # Apply Kalman filter
            meas = np.array((xpos, ypos))
            (x_new, P_new) = KalmanFilter(x_prev, P_prev, meas, F, H, Q, R)
            x_prev = x_new
            P_prev = P_new
            
            xpos = round(x_new[0], 3) #xpos = round(xpos, 3)
            ypos = round(x_new[1], 3) #ypos = round(ypos, 3)
            print("Transmitter position is:", xpos, ypos)
            time.sleep(0.1)
        elif (state == 'pause' or state == 'ini'):
            time.sleep(0.1)
        else:
            break
        
##################################################################
# Everything related to the GUI

# Class for the main functionality of the GUI
class MainMenu:
    def __init__(self, root):
        self.root = root
        # Frame for 3 buttons
        self.btnFrame = Frame(root)
        self.btnFrame.grid(row = 0, column = 0, pady = 10)
        
        # Add a start button
        self.startBtn = Button(self.btnFrame, text="Start", command=self.startApp)
        self.startBtn.grid(row = 0, column = 0, padx = WIDTH/8)

        # Add a pause button
        self.pauseBtn = Button(self.btnFrame, text="Pause", command=self.pauseApp)
        self.pauseBtn.grid(row = 0, column = 1, padx = WIDTH/8)
        #root.winfo_width()

        # Add a stop button
        self.stopBtn = Button(self.btnFrame, text="Stop", command=self.stopApp)
        self.stopBtn.grid(row = 0, column = 2, padx = WIDTH/8)

        # Frame for canvas which displays the transmitter position
        self.canvasFrame = Frame(root)
        self.canvasFrame.grid(row = 1, column = 0, pady = 10)
        canvasFrame = EnvCanvas(self.canvasFrame)

        

    # Function to start triangulation
    def startApp(self):
        global state
        print("Start application")
        state = 'run'

    # Function to pause app
    def pauseApp(self):
        global state
        print("Pause application")
        state = 'pause'

    # Function to stop app
    def stopApp(self):
        global state
        print("Stop application")
        state = 'quit'
        self.root.destroy()


# Class for drawing the environment together with the transmitter position
# NOTE: X AND Y COORDINATES ARE OPPOSITE FROM THE ONES COMPUTED WITH TRIANGULATION
# Coordinates for the antenna array are based on arbitrary positions on the lab
class EnvCanvas:
    def __init__(self, root):
        self.root = root
        
        # Add the actual canvas
        self.C = Canvas(self.root, bg = "white", height = (HEIGHT - 100), width = (WIDTH - 50))

        # Create table outline
        self.C.topleftx = 50
        self.C.toplefty = 50
        self.C.botrightx = 620
        self.C.botrighty = 330
        self.C.tableCoords = (self.C.topleftx, self.C.toplefty, self.C.botrightx, self.C.botrighty)
        self.C.table = self.C.create_rectangle(self.C.tableCoords)

        # Create a circle to display transmitter position
        self.xpos_new = self.C.topleftx + xpos
        self.ypos_new = self.C.toplefty + ypos
        self.C.TXCoords = (self.ypos_new, self.xpos_new, self.ypos_new + 5, self.xpos_new + 5)
        self.C.TX = self.C.create_oval(self.C.TXCoords)

        # Create rectangles for the positions of the antenna arrays
        self.array1Coords = (self.C.toplefty + 1*2, self.C.topleftx + 58*2, self.C.toplefty + 12*2, self.C.topleftx + 82*2)
        self.array1 = self.C.create_rectangle(self.array1Coords)

        self.array2Coords = (self.C.toplefty + 106*2, self.C.topleftx + 141*2, self.C.toplefty + 130*2, self.C.topleftx + 152*2)
        self.array2 = self.C.create_rectangle(self.array2Coords)
        
        self.C.pack()
        self.updateCanvas()

    # The root widget has a function 'after', which is called after a given amount of time, thus it can be used to update the Canvas
    # Right now, this function just needs to get the correct dx and dy for the movement.
    def updateCanvas(self):
        #print("update canvas")
        dx, dy = self.updatePosition()
        self.C.move(self.C.TX, 2*dx, 2*dy)  # Move it twice as for to maintain scaling within figure
        self.root.after(100, self.updateCanvas)

    def updatePosition(self):
        # Previous position becomes old position
        self.xpos_old = self.xpos_new
        self.ypos_old = self.ypos_new

        # Update current position
        self.xpos_new = self.C.topleftx + xpos
        self.ypos_new = self.C.toplefty + ypos 

        # Return dx and dy
        dx = (self.xpos_new - self.xpos_old)
        dy = (self.ypos_new - self.ypos_old)
        #dx = random.randint(-1,1)
        #dy = random.randint(-1,1)
        return dx, dy


def GUI():
    root = Tk()
    root.geometry('{}x{}'.format(WIDTH, HEIGHT))
    root.resizable(width = False, height = False)

    MainMenu(root)

    #threading.Thread(target=triangulation).start()

    root.mainloop()

def main():
    global xpos, ypos
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
    #threading.Thread(target = inputCheck).start() #blocks threads
    #threading.Thread(target = shutdownCheck).start()
    threading.Thread(target = computePosition).start()

    # Run the graphical user interface
    GUI()
    


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
