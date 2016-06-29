import sys
import os
from PyQt4 import QtGui, QtCore

sys.path.append(os.path.abspath(os.getcwd()+'/Globals/'))

import GlobalFunctions as f

class colorBarSlice(QtGui.QWidget):
    
    def __init__(self):
        super(colorBarSlice, self).__init__()
        self.initUI()
        
    def initUI(self):  
        self.pen=QtGui.QPen(QtGui.QColor(200,200,200))      # Set the initial pen (which draws the edge of a square)
        self.brush=QtGui.QBrush(QtGui.QColor(150,10,100))   # Set the initial brush (which sets the fill of a square) 

    def paintEvent(self, e):    # this is called whenever the Widget is resized
        qp = QtGui.QPainter()   # initialise the Painter Object
        qp.begin(self)          # Begin the painting process
        self.drawRectangle(qp)  # Call the function
        qp.end()                # End the painting process
        
    def drawRectangle(self,qp): 
        size=self.size()        # get the size of this Widget (which by default fills the parent (Layout box))
        qp.setPen(self.pen)
        qp.setBrush(self.brush) # set the brush
        qp.drawRect(0,0,size.width(),size.height())     # Draw the new rectang

    def recolor(self,qColor):
        self.pen.setColor(qColor)
        self.brush.setColor(qColor)
        self.update()