#!/usr/bin/python

from PyQt4 import QtGui, QtCore
from dock import Dock

class BlockModel(object):
    def __init__(self,imagefile="pattern.png",x=0,y=0,selected=False):
        self.x = x
        self.y = y
        self.selected = selected
        self.imagefile = imagefile
        
    def code(self):
        raise NotImplementedError
        
class BlockView(QtGui.QGraphicsItemGroup):
    
    __model__ = BlockModel
    __image__ = "motor.png"
            
    def __init__(self):
        QtGui.QGraphicsItemGroup.__init__(self)
        
        self.docks = []
        
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | \
                          QtGui.QGraphicsItem.ItemIsSelectable | \
                          QtGui.QGraphicsItem.ItemIsFocusable)
        
    #overload this method
    def setModel(self, model):
        self.model  = model
        self.pixitem = QtGui.QGraphicsPixmapItem( QtGui.QPixmap(model.imagefile) )
        self.addToGroup( self.pixitem )
        self.setPos( QtCore.QPointF(model.x, model.y) )
        self.setSelected(model.selected)
        
    #overload this method
    def updateModel(self):
        model = self.model
        self.pixitem.setPixmap( QtGui.QPixmap(model.imagefile) )
        self.setPos( QtCore.QPointF(model.x, model.y) )
        self.setSelected(model.selected)
        
    #overload this method
    def dialog(self):
        return None
    
    #overload this method
    def erase(self):
        for d in self.docks:
            d.disconnect()
    
    def addDock(self, dock):
        self.addToGroup( dock )
        self.docks.append(dock)
    
    def getChildren(self):
        l = []
        l.append(self)
        for i in self.docks:
            if i.flow == Dock.flow.TO_CHILD and i.destiny:
                l.extend( i.destiny.block.getChildren() )
        return l
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            self.model.x = value.toPointF().x()
            self.model.y = value.toPointF().y()
        elif change == QtGui.QGraphicsItem.ItemSelectedChange:
            self.model.selected = value.toBool()
        return QtGui.QGraphicsItem.itemChange(self, change, value)
        

                           
## custom blocks ##
                        
class MotorBlockModel(BlockModel):
    
    __number_motors__ = 4
    
    def __init__(self):
        BlockModel.__init__(self)
        self.imagefile = "motor.png"
        self.motors = [True,]*self.__number_motors__
        
    def code(self):
        return [self.dock_parent, self.dock_child]

class MotorBlockView(BlockView):
    
    __model__ = MotorBlockModel
    __image__ = "brake.png"
    
    def __init__(self):
        BlockView.__init__(self)
        
        self.dock_parent = Dock(self, QtCore.QRectF(20, -10, 30, 20),
        Dock.type.NORMAL, Dock.format.FEM, Dock.flow.TO_PARENT )
        self.addDock(self.dock_parent)
        
        self.dock_child  = Dock(self, QtCore.QRectF(20, 29, 30, 20),
        Dock.type.NORMAL, Dock.format.MASC, Dock.flow.TO_CHILD )
        self.addDock(self.dock_child)
        
        self.label = QtGui.QGraphicsSimpleTextItem()
        self.label.setPos(self.boundingRect().width()/2, \
                              self.boundingRect().height()/2)
        self.addToGroup( self.label )
        self.label.setZValue(1)
        
    def setModel(self, model):
        BlockView.setModel(self, model)
        self.updateLabel()

    def updateModel(self):
        BlockView.updateModel(self)
        self.updateLabel()
        
    def updateLabel(self):
        s = ""
        for i,k in enumerate(self.model.motors):
            if k: s += chr(ord('a')+i)
        self.label.setText(s)

    def dialog(self):
        d = QtGui.QDialog()
        buttonBox = \
            QtGui.QDialogButtonBox(\
            QtGui.QDialogButtonBox.Ok | \
                QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(d.accept)
        buttonBox.rejected.connect(d.reject)
        
        chkbox = [QtGui.QCheckBox()\
                      for i in\
                      range(self.model.__number_motors__)]
        mainLayout = QtGui.QVBoxLayout()
        
        def update(i):
            self.model.motors = \
                map(lambda k: k.isChecked(), chkbox)
            
        for i in chkbox:
            i.stateChanged.connect(update)
            mainLayout.addWidget(i)
        
        mainLayout.addWidget(buttonBox)
        d.setLayout(mainLayout)
        return d
