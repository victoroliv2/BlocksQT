from PyQt4 import QtGui, QtCore

class Dock(QtGui.QGraphicsRectItem):
    
    class type(object):
        ALL, NORMAL, LOGIC, NUMBER = range(4)
    
    class format(object):
        FEM, MASC = range(2)
        
    class flow(object):
        TO_PARENT, TO_CHILD = range(2)
        
    def __init__(self, block, rect, type, format, flow):
        QtGui.QGraphicsRectItem.__init__(self, rect)
        
        b = QtGui.QBrush(QtGui.QColor(255,255,255))
        self.setBrush(b)
        #self.setOpacity(0)
        
        self.destiny = None
        self.enabled = True
        self.type    = type
        self.format  = format
        self.flow    = flow
        self.rect    = rect
        self.block   = block
        
    def can_connect(self, dock2):
        if self == dock2 or self.block == dock2.block:
            return False
        
        if self.type == dock2.type and self.format != dock2.format and\
        self.enabled == True and dock2.enabled == True and self.flow != dock2.flow:
            return True
        else:
            return False

    def connect(self, dock2):
        if self.can_connect(dock2):
            
            b = QtGui.QBrush(QtGui.QColor(255,0,0))
            self.setBrush(b)
            dock2.setBrush(b)
            
            self.destiny = dock2
            self.enabled = False
            
            dock2.destiny = self
            dock2.enabled = False
            
            return True
        else:
            return False

    def disconnect(self):
        b = QtGui.QBrush(QtGui.QColor(255,255,255))
        
        if self.enabled == False:
            self.destiny.destiny = None
            self.destiny.enabled = True
            
            self.destiny.setBrush(b)
        
        self.setBrush(b)
        
        self.destiny = None
        self.enabled = True
