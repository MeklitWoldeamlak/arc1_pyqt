####################################

# (c) Radu Berdan
# ArC Instruments Ltd.

# This code is licensed under GNU v3 license (see LICENSE.txt for details)

####################################

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import time

import Globals.GlobalFonts as fonts
import Globals.GlobalFunctions as f
import Globals.GlobalVars as g
import Globals.GlobalStyles as s

tag="EN"
g.tagDict.update({tag:"Endurance"})

class getData(QtCore.QObject):

    finished=QtCore.pyqtSignal()
    sendData=QtCore.pyqtSignal(int, int, float, float, float, str)
    highlight=QtCore.pyqtSignal(int,int)
    displayData=QtCore.pyqtSignal()
    updateTree=QtCore.pyqtSignal(int, int)
    disableInterface=QtCore.pyqtSignal(bool)
    getDevices=QtCore.pyqtSignal(int)

    def __init__(self,deviceList):
        super(getData,self).__init__()
        self.deviceList=deviceList

    def getIt(self):

        self.disableInterface.emit(True)
        global tag

        g.ser.write(str(int(len(self.deviceList)))+"\n") #Tell mBED how many devices to be operated on.

        for device in self.deviceList:
            w=device[0]
            b=device[1]
            self.highlight.emit(w,b)

            g.ser.write(str(int(w))+"\n")
            g.ser.write(str(int(b))+"\n")

            firstPoint=1
            endCommand=0

            valuesNew=f.getFloats(3)
            # valuesNew.append(float(g.ser.readline().rstrip()))
            # valuesNew.append(float(g.ser.readline().rstrip()))
            # valuesNew.append(float(g.ser.readline().rstrip()))

            if (float(valuesNew[0])!=0 or float(valuesNew[1])!=0 or float(valuesNew[2])!=0):
                tag_=tag+'_s'
            else:
                endCommand=1;

            while(endCommand==0):
                valuesOld=valuesNew

                valuesNew=f.getFloats(3)
                # valuesNew.append(float(g.ser.readline().rstrip()))
                # valuesNew.append(float(g.ser.readline().rstrip()))
                # valuesNew.append(float(g.ser.readline().rstrip()))

                if (float(valuesNew[0])!=0 or float(valuesNew[1])!=0 or float(valuesNew[2])!=0):
                    self.sendData.emit(w,b,valuesOld[0],valuesOld[1],valuesOld[2],tag_)
                    self.displayData.emit()
                    tag_=tag+'_i'
                else:
                    tag_=tag+'_e'
                    self.sendData.emit(w,b,valuesOld[0],valuesOld[1],valuesOld[2],tag_)
                    self.displayData.emit()
                    endCommand=1
            self.updateTree.emit(w,b)

        self.disableInterface.emit(False)
        self.finished.emit()


class Endurance(QtWidgets.QWidget):
    
    def __init__(self, short=False):
        super(Endurance, self).__init__()
        self.short=short
        self.initUI()
        
    def initUI(self):      

        vbox1=QtWidgets.QVBoxLayout()

        titleLabel = QtWidgets.QLabel('Endurance')
        titleLabel.setFont(fonts.font1)
        descriptionLabel = QtWidgets.QLabel('Cycle the resistive state of a bistable device using alternative polarity voltage pulses, for any number of cycles.')
        descriptionLabel.setFont(fonts.font3)
        descriptionLabel.setWordWrap(True)

        isInt=QtGui.QIntValidator()
        isFloat=QtGui.QDoubleValidator()

        leftLabels=['Positive pulse amplitude (V)',\
                    'Positive pulse width (us)', \
                    'Positive current cut-off (uA)', \
                    'No. of positive pulses',\
                    'Cycles',\
                    'Interpulse time (ms)']

        rightLabels=['Negative pulse amplitude (V)',\
                    'Negative pulse width (us)', \
                    'Negative current cut-off (uA)', \
                    'No. of negative pulses']

        leftInit=  ['1',\
                    '100', \
                    '0',\
                    '1',\
                    '10',\
                    '0']

        rightInit=  ['1',\
                    '100',\
                    '0',\
                    '1']

        self.leftEdits=[]
        self.rightEdits=[]

        gridLayout=QtWidgets.QGridLayout()
        gridLayout.setColumnStretch(0,3)
        gridLayout.setColumnStretch(1,1)
        gridLayout.setColumnStretch(2,1)
        gridLayout.setColumnStretch(3,1)
        gridLayout.setColumnStretch(4,3)
        gridLayout.setColumnStretch(5,1)
        gridLayout.setColumnStretch(6,1)
        if self.short==False:
            gridLayout.setColumnStretch(7,2)
        #gridLayout.setSpacing(2)

        #setup a line separator
        lineLeft=QtWidgets.QFrame()
        lineLeft.setFrameShape(QtWidgets.QFrame.VLine);
        lineLeft.setFrameShadow(QtWidgets.QFrame.Raised);
        lineLeft.setLineWidth(1)
        #lineRight=QtWidgets.QFrame()
        #lineRight.setFrameShape(QtWidgets.QFrame.VLine);
        #lineRight.setFrameShadow(QtWidgets.QFrame.Raised);
        #lineRight.setLineWidth(1)

        gridLayout.addWidget(lineLeft, 0, 2, 6, 1)
        #gridLayout.addWidget(lineRight, 0, 6, 5, 1)

        #label1=QtWidgets.QLabel('Pulse Amplitude (V)')
        #label1.setFixedWidth(150)
        #label2=QtWidgets.QLabel('Pulse width (us)')
        #label2.setFixedWidth(150)
        #label3=QtWidgets.QLabel('Cycles')
        #label3.setFixedWidth(150)
        #label4=QtWidgets.QLabel('Interpulse (ms)')
        #label4.setFixedWidth(150)

        for i in range(len(leftLabels)):
            lineLabel=QtWidgets.QLabel()
            #lineLabel.setFixedHeight(50)
            lineLabel.setText(leftLabels[i])
            gridLayout.addWidget(lineLabel, i,0)

            lineEdit=QtWidgets.QLineEdit()
            lineEdit.setText(leftInit[i])
            lineEdit.setValidator(isFloat)
            self.leftEdits.append(lineEdit)
            gridLayout.addWidget(lineEdit, i,1)

        for i in range(len(rightLabels)):
            lineLabel=QtWidgets.QLabel()
            lineLabel.setText(rightLabels[i])
            #lineLabel.setFixedHeight(50)
            gridLayout.addWidget(lineLabel, i,4)

            lineEdit=QtWidgets.QLineEdit()
            lineEdit.setText(rightInit[i])
            lineEdit.setValidator(isFloat)
            self.rightEdits.append(lineEdit)
            gridLayout.addWidget(lineEdit, i,5)

        self.leftEdits[2].editingFinished.connect(self.imposeLimitsOnCS_p)
        self.rightEdits[2].editingFinished.connect(self.imposeLimitsOnCS_n)
        self.leftEdits[1].editingFinished.connect(self.imposeLimitsOnPW_p)
        self.rightEdits[1].editingFinished.connect(self.imposeLimitsOnPW_n)

        # verticalLine.setFrameStyle(QFrame.VLine)
        # verticalLine.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)

        vbox1.addWidget(titleLabel)
        vbox1.addWidget(descriptionLabel)

        self.vW=QtWidgets.QWidget()
        self.vW.setLayout(gridLayout)
        self.vW.setContentsMargins(0,0,0,0)

        scrlArea=QtWidgets.QScrollArea()
        scrlArea.setWidget(self.vW)
        scrlArea.setContentsMargins(0,0,0,0)
        scrlArea.setWidgetResizable(False)
        scrlArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        scrlArea.installEventFilter(self)

        vbox1.addWidget(scrlArea)
        vbox1.addStretch()

        if self.short==False:

            self.hboxProg=QtWidgets.QHBoxLayout()

            push_single=QtWidgets.QPushButton('Apply to One')
            push_range=QtWidgets.QPushButton('Apply to Range')
            push_all=QtWidgets.QPushButton('Apply to All')

            push_single.setStyleSheet(s.btnStyle)
            push_range.setStyleSheet(s.btnStyle)
            push_all.setStyleSheet(s.btnStyle)

            push_single.clicked.connect(self.programOne)
            push_range.clicked.connect(self.programRange)
            push_all.clicked.connect(self.programAll)

            self.hboxProg.addWidget(push_single)
            self.hboxProg.addWidget(push_range)
            self.hboxProg.addWidget(push_all)

            vbox1.addLayout(self.hboxProg)

        self.setLayout(vbox1)
        self.gridLayout=gridLayout

    def imposeLimitsOnPW_p(self):   # if pw is set to below 30us and current cut-off is activated, increase pulse width to 30us
        if float(self.leftEdits[2].text())!=0 and float(self.leftEdits[1].text())<30:
            self.leftEdits[1].setText("30")

    def imposeLimitsOnPW_n(self): # if pw is set to below 30us and current cut-off is activated, increase pulse width to 30us
        if float(self.rightEdits[2].text())!=0 and float(self.rightEdits[1].text())<30:
            self.rightEdits[1].setText("30")


    def imposeLimitsOnCS_p(self):   # if current cut-off is set, make sure values are between 10 and 1000 uA. Also, increase pw to a minimum of 30 us.
        currentText=float(self.leftEdits[2].text())
        if currentText!=0:
            if currentText<10:
                self.leftEdits[2].setText("10")
            if currentText>1000:
                self.leftEdits[2].setText("1000")
            if float(self.leftEdits[1].text())<30:
                self.leftEdits[1].setText("30")


    def imposeLimitsOnCS_n(self,): # if current cut-off is set, make sure values are between 10 and 1000 uA. Also, increase pw to a minimum of 30 us.
        currentText=float(self.rightEdits[2].text())
        if currentText!=0:
            if currentText<10:
                self.rightEdits[2].setText("10")
            if currentText>1000:
                self.rightEdits[2].setText("1000")
            if float(self.leftEdits[1].text())<30:
                self.rightEdits[1].setText("30")


    def extractPanelParameters(self):
        layoutItems=[[i,self.gridLayout.itemAt(i).widget()] for i in range(self.gridLayout.count())]
        
        layoutWidgets=[]

        for i,item in layoutItems:
            if isinstance(item, QtWidgets.QLineEdit):
                layoutWidgets.append([i,'QLineEdit', item.text()])
            if isinstance(item, QtWidgets.QComboBox):
                layoutWidgets.append([i,'QComboBox', item.currentIndex()])
            if isinstance(item, QtWidgets.QCheckBox):
                layoutWidgets.append([i,'QCheckBox', item.checkState()])

        return layoutWidgets

    def setPanelParameters(self, layoutWidgets):
        for i,type,value in layoutWidgets:
            if type=='QLineEdit':
                self.gridLayout.itemAt(i).widget().setText(value)
            if type=='QComboBox':
                self.gridLayout.itemAt(i).widget().setCurrentIndex(value)
            if type=='QCheckBox':
                self.gridLayout.itemAt(i).widget().setChecked(value)

    def eventFilter(self, object, event):
        if event.type()==QtCore.QEvent.Resize:
            self.vW.setFixedWidth(event.size().width()-object.verticalScrollBar().width())
        return False

    def sendParams(self):
        g.ser.write(str(float(self.leftEdits[0].text()))+"\n")              # send positive amplitude
        g.ser.write(str(float(self.leftEdits[1].text())/1000000)+"\n")      # send positive pw
        g.ser.write(str(float(self.leftEdits[2].text())/1000000)+"\n")      # send positive cut-off (A)
        #time.sleep(0.001)
        g.ser.write(str(float(self.rightEdits[0].text())*-1)+"\n")          # send negative amplitude
        g.ser.write(str(float(self.rightEdits[1].text())/1000000)+"\n")     # send negative pw
        g.ser.write(str(float(self.rightEdits[2].text())/1000000)+"\n")     # send negative cut-off (A)
        #time.sleep(0.001)
        g.ser.write(str(float(self.leftEdits[5].text()))+"\n")              # send interpulse (ms)

        g.ser.write(str(int(self.leftEdits[3].text()))+"\n")              # send positive nr of pulses
        g.ser.write(str(int(self.rightEdits[3].text()))+"\n")             # send negative nr of pulses
        g.ser.write(str(int(self.leftEdits[4].text()))+"\n")              # send cycles
        #time.sleep(0.001)


    def programOne(self):
        if g.ser.port != None:
            job="191"
            g.ser.write(job+"\n")   # sends the job

            self.sendParams()

            self.thread=QtCore.QThread()
            self.getData=getData([[g.w,g.b]])
            self.finalise_thread_initialisation()

            self.thread.start()

    def disableProgPanel(self,state):
        if state==True:
            self.hboxProg.setEnabled(False)
        else:
            self.hboxProg.setEnabled(True)


    def programRange(self):
        if g.ser.port != None:
            rangeDev=self.makeDeviceList(True)


            job="191"
            g.ser.write(job+"\n")   # sends the job

            self.sendParams()

            self.thread=QtCore.QThread()
            self.getData=getData(rangeDev)
            self.finalise_thread_initialisation()

            self.thread.start()
        

    def programAll(self):
        if g.ser.port != None:
            rangeDev=self.makeDeviceList(False)

            job="191"
            g.ser.write(job+"\n")   # sends the job

            self.sendParams()

            self.thread=QtCore.QThread()
            self.getData=getData(rangeDev)
            self.finalise_thread_initialisation()

            self.thread.start()

    def finalise_thread_initialisation(self):
        self.getData.moveToThread(self.thread)
        self.thread.started.connect(self.getData.getIt)
        self.getData.finished.connect(self.thread.quit)
        self.getData.finished.connect(self.getData.deleteLater)
        self.thread.finished.connect(self.getData.deleteLater)
        self.getData.sendData.connect(f.updateHistory)
        self.getData.highlight.connect(f.cbAntenna.cast)
        self.getData.displayData.connect(f.displayUpdate.cast)
        self.getData.updateTree.connect(f.historyTreeAntenna.updateTree.emit)
        self.getData.disableInterface.connect(f.interfaceAntenna.cast)     
        self.thread.finished.connect(f.interfaceAntenna.wakeUp)   

    def makeDeviceList(self,isRange):
        #if g.checkSA=False:
        rangeDev=[] # initialise list which will contain the SA devices contained in the user selected range of devices
        #rangeMax=0;
        if isRange==False:
            minW=1
            maxW=g.wline_nr
            minB=1
            maxB=g.bline_nr
        else:
            minW=g.minW
            maxW=g.maxW
            minB=g.minB
            maxB=g.maxB            


        # Find how many SA devices are contained in the range
        if g.checkSA==False:
            for w in range(minW,maxW+1):
                for b in range(minB,maxB+1):
                    rangeDev.append([w,b])
            #rangeMax=(wMax-wMin+1)*(bMax-bMin+1)
        else:
            for w in range(minW,maxW+1):
                for b in range(minB,maxB+1):
                    for cell in g.customArray:
                        if (cell[0]==w and cell[1]==b):
                            rangeDev.append(cell)

        return rangeDev

