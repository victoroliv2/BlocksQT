#!/usr/bin/python

import sys, random, pickle
from PyQt4 import QtGui, QtCore
from commands import *

class BlockGraphicsScene(QtGui.QGraphicsScene):
    
    typename = {}
    
    def __init__(self, parent=None):
        QtGui.QGraphicsScene.__init__(self, parent)
        
        self.img0 = BlockView( BlockModel() )
        self.img1 = MotorBlockView( MotorBlockModel() )
        self.img2 = MotorBlockView( MotorBlockModel() )
        self.img3 = MotorBlockView( MotorBlockModel() )
        self.img4 = MotorBlockView( MotorBlockModel() )
        
        self.addItem(self.img1)
        self.addItem(self.img2)
        self.addItem(self.img3)
        self.addItem(self.img4)
        self.addItem(self.img0)
        
    @staticmethod
    def register( typename ):
        BlockGraphicsScene.typename[typename.__name__] = typename
        BlockGraphicsScene.typename[typename] = typename.__name__
        
    def blocks(self):
        return [i for i in self.items() if issubclass(type(i), BlockView)]
        
    def selectedBlocks(self):
        return [i for i in self.selectedItems() if issubclass(type(i), BlockView)]
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for i in self.selectedBlocks():
                i.erase()
                self.removeItem(i)
        elif event.key() == QtCore.Qt.Key_L:
            self.load('test.sv')
        elif event.key() == QtCore.Qt.Key_S:
            self.save('test.sv')
            
    def save(self, f):
        a = open(f, 'w')
        l = []
        for i in self.blocks():
            k = (type(i), i.model)
            l.append(k)
        pickle.dump(l, a)
        a.close()
    
    def load(self, f):
        self.clear()
        a = open(f, 'r')
        l = pickle.load(a)
        for t,m in l:
            block = t(m)
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
        
        BlockGraphicsScene.register( BlockView )
        BlockGraphicsScene.register( MotorBlockView )
        
        dt = BlockGraphicsView()
        
        frameLayout.addWidget(blist)
        frameLayout.addWidget(dt)
        self.setCentralWidget(frame)
        
app = QtGui.QApplication(sys.argv)


m = MainWindow()
m.show()

app.exec_()
