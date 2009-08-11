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
    
    class commandMove(QtGui.QUndoCommand):
        def __init__(self, blocklist, pos):
            QtGui.QUndoCommand.__init__("block move")
            self.blocklist = blocklist
            self.pos = pos
            
        def redo(self):
            for i in self.blocklist:
                i.moveBy(self.pos.x(), self.pos.y())

        def undo(self):
            for i in self.blocklist:
                i.moveBy(-self.pos.x(), -self.pos.y())
            
    def __init__(self, model):
        QtGui.QGraphicsItemGroup.__init__(self)
        
        self.model = model
        self.docks = []
        
        self.pixmap = QtGui.QPixmap(model.imagefile)
        self.addToGroup( QtGui.QGraphicsPixmapItem(self.pixmap) )
        
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsFocusable)
        self.setPos( QtCore.QPointF(model.x, model.y) )
        self.setSelected(model.selected)
    
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
        
    def mousePressEvent(self, event):
        QtGui.QGraphicsItemGroup.mousePressEvent(self, event)
        
        for i in self.getChildren(): i.setSelected(True)
        
        for i in self.scene().selectedBlocks():
            for d in i.docks:
                if (d.destiny and not d.destiny.block.isSelected()):
                    d.disconnect()
        
    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self, event)
        
        for block in self.scene().selectedBlocks():
            for d in block.docks:
                if (not d.destiny) or\
                (d.destiny and not d.destiny.block.isSelected()):
                    d.disconnect()
                    l = [i for i in d.collidingItems() if isinstance(i, Dock)]
                    for d2 in l:
                        if d.connect(d2):
                           k = d2.scenePos()+d2.rect.bottomLeft() - \
                           d.scenePos()-d.rect.bottomLeft()
                           for i in self.scene().selectedBlocks():
                               i.moveBy(k.x(), k.y())
                           return
                           
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
    
    def __init__(self, model):
        BlockView.__init__(self, model)
        
        self.dock_parent = Dock(self, QtCore.QRectF(20, -10, 30, 20),
        Dock.type.NORMAL, Dock.format.FEM, Dock.flow.TO_PARENT )
        self.addDock(self.dock_parent)
        
        self.dock_child  = Dock(self, QtCore.QRectF(20, 29, 30, 20),
        Dock.type.NORMAL, Dock.format.MASC, Dock.flow.TO_CHILD )
        self.addDock(self.dock_child)
        
        self.label = QtGui.QGraphicsSimpleTextItem()
        self.label.setPos(self.boundingRect().width()/2, self.boundingRect().height()/2)
        self.addToGroup( self.label )
        self.label.setZValue(1)
        
        self.updateLabel()
        
    def updateLabel(self):
        s = ""
        for i,k in enumerate(self.model.motors):
            if k: s += chr(ord('a')+i)
        self.label.setText(s)
