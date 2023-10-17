from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import QTimeLine, QRect, Qt, QTimer
import sys
import numpy as np
import pyqtgraph as pg
import random

from queue import Queue

class ColorBar(QWidget):
    def __init__(self,parent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rect = []
        self.color = []   

        self.setWindowTitle("dynamic colorbar") 
        self.resize(1800, 1800)

        

    def ChooseColor(self, data):
        if data == 0:
            color = QColor(0,225,225)
        if data == 1:
            color = QColor(225,225, 0)
        if data == 2:
            color = QColor(225, 0, 225)
        return color
    
    def DrawRectangle(self, data):
        brush = QBrush(Qt.SolidPattern)
        ## move right
        self.rect.pop()
        self.color.pop()
        for i in range(0, self.max_size-1):
            brush.setColor(self.color[i])
            self.painter.setBrush(brush)
            rect = QRect(300+self.width*(i+1), 500, self.width, self.height)
            print("i: ", i)
            self.painter.drawRect(rect)
        ## render new color
        color = self.ChooseColor(data)
        self.color.insert(0, color)
        # print("color: ", color)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(color)
        self.painter.setBrush(brush)
        rect = QRect(300, 500, self.width, self.height)
        self.rect.insert(0, rect)
        self.painter.drawRect(rect)
        
    #从外部获取队列
    def setData(self, data, max_size, width, height):
        self.width = width
        self.height = height
        self.data = data
        self.max_size = max_size

    def paintEvent(self, event):
        ### base
        if self.data.qsize() == 0:
            self.painter_base = QPainter()
            self.painter_base.begin(self)
            self.painter_base.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            for i in range(0, self.max_size):
                brush = QBrush(Qt.SolidPattern)
                brush.setColor(QColor(255,255,255))
                self.painter_base.setBrush(brush)
                rect = QRect(300+self.width*i, 500, self.width, self.height)
                # rect.setColor(Qt.blue)
                self.rect.append(rect)
                self.color.append(QColor(255,255,255))
                self.painter_base.drawRect(rect)
            self.painter_base.end()
        else:
            ### dynamic
            self.painter = QPainter()#画图类
            self.painter.begin(self)
            self.painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            data = self.data.queue[-1]
            print("data: ", data)
            self.DrawRectangle(data)
            # print("data: ", self.data.queue[-1])
            # color = self.ChooseColor(self.data.queue[-1])

            self.painter.end()


class Windows(QWidget):
    def __init__(self, max_size, width, height):
        super().__init__()
        self.max_size = max_size
        self.width = width
        self.height = height  
        self.data = Queue()
        self.setWindowTitle("plot") 
        self.resize(1800, 1800)
        self.setup_ui() 
    
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def setup_ui(self):
        self.colorbar = ColorBar(self)
        self.colorbar.setData(self.data, self.max_size, self.width, self.height)
        self.colorbar.resize(2800,1800)
        # self.colorbar.move(100,100)

    def update(self):
        tdata = random.randint(0,2)
        if self.data.qsize() > self.max_size:
            print("queue oversize!")
        elif self.data.qsize() == self.max_size:
            _ = self.data.get()
        if self.data.qsize() < self.max_size:
            self.data.put(tdata)  ### 插入队尾

        self.colorbar.setData(self.data, self.max_size, self.width, self.height)
        self.colorbar.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    max_size = 30
    window = Windows(max_size, 60, 30)
    window.show()
    sys.exit(app.exec_())


