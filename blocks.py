#!/usr/bin/python

import sys, random, pickle
from PyQt4 import QtGui, QtCore
from commands import *

class BlockGraphicsScene(QtGui.QGraphicsScene):
    
    typename = {}
    
    class commandMove(QtGui.QUndoCommand):
        def __init__(self, scene, blocklist, startpos, endpos):
            super(BlockGraphicsScene.commandMove, self).__init__("")
            self.blocklist = blocklist
            self.startpos  = startpos
            self.endpos    = endpos
            self.scene     = scene
        def redo(self):
            for i,block in enumerate(self.blocklist):
                endpos = self.endpos[i]
                block.setPos(endpos.x(), endpos.y())
            self.scene.updateDocks()

        def undo(self):
            for i,block in enumerate(self.blocklist):
                startpos = self.startpos[i]
                block.setPos(startpos.x(), startpos.y())
            self.scene.updateDocks()
                
    def __init__(self, parent=None):
        QtGui.QGraphicsScene.__init__(self, parent)
        self.undostack = QtGui.QUndoStack()
                
    @staticmethod
    def register( typename ):
        BlockGraphicsScene.typename[typename.__name__] = typename
        BlockGraphicsScene.typename[typename] = typename.__name__
        
    def blocks(self):
        return [i for i in self.items() if issubclass(type(i), BlockView)]
        
    def selectedBlocks(self):
        return [i for i in self.selectedItems() if issubclass(type(i), BlockView)]
        
    def mousePressEvent(self, event):
        QtGui.QGraphicsScene.mousePressEvent(self, event)
        block = self.getBlock( event.scenePos() )
        if block:
            for i in block.getChildren(): i.setSelected(True)

            for i in self.selectedBlocks():
                i.startpos = i.scenePos()

            for i in self.selectedBlocks():
                for d in i.docks:
                    if (d.destiny and not d.destiny.block.isSelected()):
                        d.disconnect()
    
    def mouseDoubleClickEvent(self, event):
        block = self.getBlock( event.scenePos() )
        if block:
            dialog = block.dialog()
            if dialog:
                dialog.exec_()
                block.updateModel()
                
    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsScene.mouseReleaseEvent(self, event)
        
        for block in self.selectedBlocks():
            for d in block.docks:
                if (not d.destiny) or\
                (d.destiny and not d.destiny.block.isSelected()):
                    d.disconnect()
                    l = [i for i in d.collidingItems() if isinstance(i, Dock)]
                    for d2 in l:
                        if d.connect(d2):
                           k = d2.scenePos()+d2.rect.bottomLeft() - \
                           d.scenePos()-d.rect.bottomLeft()
                           
                           cm = self.commandMove(self, self.selectedBlocks(),\
                           [b.startpos     for b in self.selectedBlocks()],\
                           [b.scenePos()+k for b in self.selectedBlocks()])
                           
                           self.undostack.push(cm)
                           return
                           
        cm = self.commandMove(self, self.selectedBlocks(),\
        [b.startpos   for b in self.selectedBlocks()],\
        [b.scenePos() for b in self.selectedBlocks()])
        self.undostack.push(cm)
        
    def getBlock(self, pos):
        block = self.itemAt( pos )
        if not block in [0, None]:
            try:
                block = block.group() or block
            except AttributeError:
                block = None
        return block
        
    def updateDocks(self):
        for block in self.blocks():
            for d in block.docks:
                d.disconnect()
                l = [i for i in d.collidingItems() if isinstance(i, Dock)]
                for d2 in l:
                    if d.scenePos()+d.rect.bottomLeft() == d2.scenePos()+d2.rect.bottomLeft():
                        d.connect(d2)
                        break
                        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for i in self.selectedBlocks():
                i.erase()
                self.removeItem(i)
        elif event.key() == QtCore.Qt.Key_L:
            self.load('test.sv')
        elif event.key() == QtCore.Qt.Key_S:
            self.save('test.sv')
        elif event.key() == QtCore.Qt.Key_U:
            self.undostack.undo()
        elif event.key() == QtCore.Qt.Key_R:
            self.undostack.redo()
            
    def save(self, f):
        print 'save'
        a = open(f, 'w')
        l = []
        for i in self.blocks():
            k = (type(i), i.model)
            l.append(k)
        pickle.dump(l, a)
        a.close()
    
    def load(self, f):
        print 'load'
        self.clear()
        a = open(f, 'r')
        l = pickle.load(a)
        for t,m in l:
            block = t()
            block.setModel(m)
            self.addItem(block)
        a.close()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('image/x-block'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('image/x-block'):
            #event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('image/x-block'):
            blockData = event.mimeData().data('image/x-block')
            stream = QtCore.QDataStream(blockData, QtCore.QIODevice.ReadOnly)
            s = QtCore.QString()
            stream >> s
            blockview = BlockGraphicsScene.typename[str(s)]
            
            b = blockview( blockview.__model__() )
            b.setPos( event.scenePos() )
            self.addItem( b )
            
            event.accept()
        else:
            event.ignore()

class BlockGraphicsView(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        
        self.scene = BlockGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.scale (1.5, 1.5)
        back = QtGui.QBrush(QtGui.QColor(128,128,128), QtCore.Qt.NoBrush)
        back.setTexture( QtGui.QPixmap('pattern.png') )
        self.setBackgroundBrush (back)

class BlockListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        
        self.setDragEnabled(True)
        self.setViewMode(QtGui.QListView.ListMode)
        self.setIconSize(QtCore.QSize(1000, 1000))
        self.setSpacing(10)
        self.setMovement(QtGui.QListView.Free)
        #self.setAcceptDrops(True)
        #self.setDropIndicatorShown(True)
        
    def addBlock(self, blocktype):
        pixmap = QtGui.QPixmap(blocktype.__image__)
        blockItem = QtGui.QListWidgetItem(self)
        blockItem.setIcon(QtGui.QIcon(pixmap))
        blockItem.setData(QtCore.Qt.UserRole, QtCore.QVariant(pixmap))
        blockItem.setData(QtCore.Qt.UserRole+1, QtCore.QVariant(QtCore.QString(blocktype.__name__)) )
        blockItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
        
    def startDrag(self, supportedActions):
        item = self.currentItem()
        
        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        
        pixmap   = QtGui.QPixmap( item.data(QtCore.Qt.UserRole) )
        typename = item.data(QtCore.Qt.UserRole+1).toString()
        
        dataStream << typename
        
        mimeData = QtCore.QMimeData()
        mimeData.setData('image/x-block', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.exec_()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('image/x-block'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('image/x-block'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        frame = QtGui.QFrame()
        frameLayout = QtGui.QHBoxLayout(frame)
        
        blist = BlockListWidget()
        blist.addBlock( BlockView )
        blist.addBlock( MotorBlockView )
        blist.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored )
        
        BlockGraphicsScene.register( BlockView )
        BlockGraphicsScene.register( MotorBlockView )
        
        bv = BlockGraphicsView()
        
        img0 = BlockView()
        img0.setModel(BlockModel())
        img1 = MotorBlockView()
        img1.setModel(MotorBlockModel())
        img2 = MotorBlockView()
        img2.setModel(MotorBlockModel())
        img3 = MotorBlockView()
        img3.setModel(MotorBlockModel())
        img4 = MotorBlockView()
        img4.setModel(MotorBlockModel())
        
        bv.scene.addItem(img1)
        bv.scene.addItem(img2)
        bv.scene.addItem(img3)
        bv.scene.addItem(img4)
        bv.scene.addItem(img0)

        frameLayout.addWidget(blist)
        frameLayout.addWidget(bv)
        self.setCentralWidget(frame)
        
app = QtGui.QApplication(sys.argv)


m = MainWindow()
m.show()

app.exec_()
