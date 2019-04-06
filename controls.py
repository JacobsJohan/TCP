from tkinter import *
import time
import random
import threading
import Host

# GUI dimensions
WIDTH = 720
HEIGHT = 480

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

        

    # Function to start app
    def startApp(self):
        print("Start application")

    # Function to pause app
    def pauseApp(self):
        print("Pause application")

    # Function to stop app
    def stopApp(self):
        print("Stop application")


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
        self.xpos_new = self.C.topleftx + Host.xpos
        self.ypos_new = self.C.toplefty + Host.ypos
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
        self.xpos_new = self.C.topleftx + Host.xpos
        self.ypos_new = self.C.toplefty + Host.ypos 

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

    


if __name__ == '__main__':
    GUI()


# Deprecated: this was a test function to randomly move transmitter
'''
def triangulation():
    global xpos, ypos
    while True:
        xpos = xpos + random.randint(-1, 1)
        ypos = ypos + random.randint(-1, 1)
        time.sleep(0.1)
'''
