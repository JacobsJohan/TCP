import SharedFunctions as sf
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
import json
from Tkinter import *
import random
from decimal import Decimal

# Main variables
radioList = []
state = 'ini'     # Can be 'run', 'pause' or 'quit' (or 'ini' for initial state)
xpos = 0
ypos = 0

# GUI dimensions
WIDTH = 720
HEIGHT = 480

# Kalman filter parameters
filtering = 'EKF'  # noKalman, Kalman, Kalman_v, EKF
# Without velocity
if filtering == 'Kalman':
    F = np.identity(2)
    H = np.identity(2)
    P_prev = np.identity(2)
    x_prev = np.array(([0], [0]))
    R = np.identity(2)
    Q = np.identity(2)*0.1
elif filtering == 'Kalman_v':
    # With velocity
    dt = 0.1
    F = np.array([[1, 0, dt, 0], [0, 1, dt, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
    P_prev = np.identity(4)
    x_prev = np.array(([0], [0], [0], [0]))
    R = np.identity(2)

    var_ax = 1.6
    var_ay = 1.6
    Q = np.array([[var_ax*pow(dt,2)/4, 0, var_ax*pow(dt,3)/2, 0],
                  [0, var_ay * pow(dt, 2) / 4, 0, var_ay * pow(dt, 3) / 2],
                  [var_ax*pow(dt,3)/2, 0, var_ax*pow(dt,2), 0],
                  [0, var_ay*pow(dt,3)/2, 0, var_ay*pow(dt,2)]])
elif filtering == 'EKF':
    dt = 0.2
    F = np.array([[1, 0, dt, 0], [0, 1, dt, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    H = np.zeros((2,4))
    P_prev = np.identity(4)
    x_prev = np.zeros((4,1))
    #x_prev[0,0] = 114.49
    #x_prev[1,0] = 128.74
    R = pow((np.pi/6), 2)*np.identity(2)
    var_ax = 1.6
    var_ay = 1.6
    Q = np.array([[var_ax*pow(dt,2)/4, 0, var_ax*pow(dt,3)/2, 0],
                  [0, var_ay * pow(dt, 2) / 4, 0, var_ay * pow(dt, 3) / 2],
                  [var_ax*pow(dt,3)/2, 0, var_ax*pow(dt,2), 0],
                  [0, var_ay*pow(dt,3)/2, 0, var_ay*pow(dt,2)]])

else:
    pass

# Create a radio object for each receiver anchor that is used
class Radio:
    def __init__(self, ip, port, x, y, orientation):
        #print("Creating radio")
        self.ip = ip                    # Anchor IP-address
        self.port = port                # Anchor Port (can be used to discriminate anchors on a single PC)
        self.x = x                      # Anchor position
        self.y = y
        self.aoa = 0                    # Initial AoA is 0
        self.timestamp = 0              # Timestamp of the last AoA
        self.orientation = orientation  # Relative orientation for triangulation

# Function to read config file. On each line of the config file should be a dictionary with the anchor IP, x-position and y-position
def readConfig(filename):
    with open(filename, 'r') as f:
        for line in f:
            Dict = json.loads(line)
            radio = Radio(Dict['ip'], Dict['port'], Dict['x'], Dict['y'], Dict['orientation'])
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


# Find the connected device by comparing the IP that connected with the known IPs from the radioList
# TEMPORARY FUNCTION: because we are currently launching 2 clients from the
# same laptop, they will have the same IP, so use ports instead
def getRadio_port(port):
    # Start of by checking if the radio exists
    for radio in radioList:
        if (port == radio.port):
            return radio

    # If previous loop does not find the radio, create a new one and return it
    print("Unknown connection from port", port)
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
    radio = getRadio_port(port)
    if (radio == -1):
        print("Shutting down")
        return -1

    # Tell client to run GRC
    command = 'GRC'
    conn.sendall(command.encode('utf-8'))

    # Wait 10s to ensure everything is up and running
    time.sleep(10)
    

    # Now that everything is up and running, continuously ask for the AoA
    while (state != 'quit'):
        s.listen(1)                   # The 1 specifies the backlog parameter which is the amount of allowed connections
        conn, addr = s.accept()       # conn = a new socket to send/rcv data; addr = the address on the other end

        command = 'AoA'
        conn.sendall(command.encode('utf-8'))

        message_enc = conn.recv(1024)
        message_dec = message_enc.decode('utf-8')
        messageList = message_dec.strip(' ()\n').split(',')
        AoA = Decimal(messageList[0])

        # only compute dt for 1 anchor
        ''' Not needed for anything
        if port == 5000:
            timestampNew = Decimal((messageList[1]))
            dt = abs(timestampNew - timestampOld)
            timestampOld = timestampNew
            #print(dt)
        '''
        radio.aoa = float(AoA)
        # This sleep is here to smoothen TCP.
        # If too many requests are made per second, then the TCP connection tends to break, making the system crash.
        time.sleep(0.01)
        
    # When running = False, send message to client to shut down
    s.listen(1)
    conn, addr = s.accept()
    command = 'Shut down'
    print('Commanding clients to shut down')
    conn.sendall(command.encode('utf-8'))
    time.sleep(1)
        


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


# Perform triangulation based on the AoA from n anchors. The amount of anchors used is defined by the amount of entries
# in the config.txt file
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
        x = x + X[i]
        y = y + Y[i]
        n = n + 1
    x = x/n
    y = y/n
    return (x, y)

# Write position to file to analyse a bit later on
def posToFile(filename, xpos_, ypos_):
    text = "(" + str(xpos_) + "," + str(ypos_) + ")\n"
    with open(filename, 'a+') as f:
        f.write(text)

# Write a variable to a file (e.g. the aoa)
def varToFile(filename, var):
    text = str(var) + "\n"
    with open(filename, 'a+') as f:
        f.write(text)

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
    return (x_new, P_new)
    
 
# Extended Kalman filter for a system with unknown input. Measurements are the AoAs
# Important: set initial x_prev equal to initial measured position 
# i.e. don't start filtering before you sort of have an idea of the TX position
# This gives way better results
def EKF_function(x_prev, P_prev, y, F, H, Q, R):
    # Constants needed for the function
    xrig1 = radioList[0].x
    yrig1 = radioList[0].y
    xrig2 = radioList[1].x
    yrig2 = radioList[1].y

    # Prediction step
    x_hat = np.matmul(F, x_prev)
    print(x_hat)
    P_hat = np.matmul(np.matmul(F, P_prev), F.T) + Q

    # Fill in H
    H[0,0] = -(x_hat[1,0]-yrig1) / (pow(x_hat[0,0]-xrig1, 2) + pow(x_hat[1,0]-yrig1, 2));
    H[0,1] = (x_hat[0,0]-xrig1) / (pow(x_hat[0,0]-xrig1, 2) + pow(x_hat[1,0]-yrig1, 2));
    H[1,0] = -(x_hat[1,0]-yrig2) / (pow(x_hat[0,0]-xrig2, 2) + pow(x_hat[1,0]-yrig2, 2));
    H[1,1] = (x_hat[0,0]-xrig2) / (pow(x_hat[0,0]-xrig2, 2) + pow(x_hat[1,0]-yrig2, 2));

    # Innovation step
    S = np.matmul(np.matmul(H, P_hat), H.T) + R
    K = np.matmul(np.matmul(P_hat, H.T), np.linalg.inv(S))
    P_new = np.matmul((np.identity(K.shape[0]) - np.matmul(K, H)), P_hat)

    # Residual has updated formula
    h = np.zeros((2,1))
    h[0,0] = np.arctan((x_hat[1,0]-yrig1)/(x_hat[0,0]-xrig1))
    if (h[0,0] < 0):
        h[0,0] = h[0,0] + np.pi
    h[1,0] = np.arctan((x_hat[1,0]-yrig2)/(x_hat[0,0]-xrig2))

    y_tilde = y - h
    x_new = x_hat + np.matmul(K, y_tilde)
    return (x_new, P_new)


# Continuosly compute the position of the transmitter, unless the system is paused.
def computePosition():
    global xpos, ypos, x_prev, P_prev

    # Continuously perform triangulation
    while True:
        if (state == 'run'):
            if (filtering == 'EKF'):
                aoa1 = np.deg2rad(radioList[0].aoa)
                aoa2 = np.deg2rad(radioList[1].aoa) - np.pi/2
                meas = np.array(([aoa1], [aoa2]))
                (x_new, P_new) = EKF_function(x_prev, P_prev, meas, F, H, Q, R)
                x_prev = x_new
                P_prev = P_new
                xpos = round(x_new[0], 3)
                ypos = round(x_new[1], 3)

            else:
                (xpos, ypos) = triangulate_n()

                if (filtering == 'Kalman' or filtering == 'Kalman_v'):
                    meas = np.array(([xpos], [ypos]))
                    (x_new, P_new) = KalmanFilter(x_prev, P_prev, meas, F, H, Q, R)
                    x_prev = x_new
                    P_prev = P_new
                    xpos = round(x_new[0], 3)
                    ypos = round(x_new[1], 3)

                else:
                    xpos = round(xpos, 3)
                    ypos = round(ypos, 3)

            print("Transmitter position is:", xpos, ypos)
            time.sleep(0.1)
        elif (state == 'pause' or state == 'ini'):
            time.sleep(0.1)
        else:
            break

##################################################################
#              Everything related to the GUI                     #
##################################################################

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
        self.xpos_old = self.C.topleftx + xpos
        self.ypos_old = self.C.topleftx + ypos
        self.xpos_new = self.C.topleftx + xpos
        self.ypos_new = self.C.toplefty + ypos
        self.C.TXCoords = (self.ypos_new, self.xpos_new, self.ypos_new + 5, self.xpos_new + 5)
        self.C.TX = self.C.create_oval(self.C.TXCoords)

        # Create counter object (used to count how often a new AoA is very far away)
        self.counter = 0

        # Create rectangles for the positions of the antenna arrays
        self.array1Coords = (self.C.toplefty + 1*2, self.C.topleftx + 58*2, self.C.toplefty + 12*2, self.C.topleftx + 82*2)
        self.array1 = self.C.create_rectangle(self.array1Coords)

        self.array2Coords = (self.C.toplefty + 106*2, self.C.topleftx + 141*2, self.C.toplefty + 130*2, self.C.topleftx + 152*2)
        self.array2 = self.C.create_rectangle(self.array2Coords)

        # Draw a scale
        self.scale = self.C.create_line(50, 340, 70, 340)
        self.C.itemconfig(self.scale, fill='blue')

        self.C.pack()
        self.updateCanvas()

    # The root widget has a function 'after', which is called after a given amount of time, thus it can be used to update the Canvas
    # Right now, this function just needs to get the correct dx and dy for the movement.
    def updateCanvas(self):
        #print("update canvas")
        dx, dy = self.updatePosition()
        self.C.move(self.C.TX, 2*dy, 2*dx)  # Move it twice as much to maintain scaling within figure
        self.root.after(100, self.updateCanvas)

    def updatePosition(self):
        #return 0,0
        # Update current position
        self.xpos_new = self.C.topleftx + xpos
        self.ypos_new = self.C.toplefty + ypos

        '''
        # Check if new position is very far away, which is the case if AoA was incorrect
        if (abs(self.xpos_old - self.xpos_new) > 50 or abs(self.ypos_old - self.ypos_new) > 50):
            self.counter += 1
            # If this happens more than 5 times, then the position probably did change that much.
            # Reset counter and compute dx, dy
            if (self.counter > 4):
                pass
            else:
                return 0, 0
        #print("updating position")
        # Reset counter
        self.counter = 0
        '''

        # Return dx and dy
        dx = (self.xpos_new - self.xpos_old)
        dy = (self.ypos_new - self.ypos_old)
        #dx = random.randint(-1,1)
        #dy = random.randint(-1,1)
        
        # Previous position becomes old position
        self.xpos_old = self.xpos_new
        self.ypos_old = self.ypos_new
        
        return dx, dy


def GUI():
    root = Tk()
    root.geometry('{}x{}'.format(WIDTH, HEIGHT))
    root.resizable(width = False, height = False)

    MainMenu(root)

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

    # Start the thread to compute the transmitter position. Nothing will happen until the start button is pressed.
    threading.Thread(target = computePosition).start()

    # Run the graphical user interface
    GUI()
    


if __name__ == '__main__':
    main()