from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QAction
from WindowDemo import Ui_MainWindow
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon
from PyQt5.QtMultimedia import QMediaContent,QMediaPlayer
from PyQt5.QtCore import pyqtSlot,QUrl,QDir, QFileInfo,Qt,QEvent
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtGui import QFont, QEnterEvent, QPainter, QColor, QPen, QBrush
from plot import Windows
import sys
import os
from threading import Thread
import cv2, imutils
import time
import random
from queue import Queue


def cvImgtoQtImg(cvImg):  # 定义opencv图像转PyQt图像的函数
    QtImgBuf = cv2.cvtColor(cvImg, cv2.COLOR_BGR2BGRA)
    QtImg = QtGui.QImage(QtImgBuf.data, QtImgBuf.shape[1], QtImgBuf.shape[0], QtGui.QImage.Format_RGB32)
    return QtImg

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # self.setupUi(self)
        self.bClose1 = False
        self.bClose2 = False
        self.stop_flag = 0
        self.ui=Ui_MainWindow()    #创建UI对象
        self.ui.setupUi(self)      #构造UI界面
        # style 1: window can be stretched
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.data1 = Queue()
        self.data2 = Queue()
        self.data3 = Queue()
        # style 2: window can not be stretched
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint
        #                     | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        # self.setWindowOpacity(0.85)  # Transparency of window
        

        self.screen1 = self.ui.label2
        self.screen2 = self.ui.label_3
        self.screen3 = self.ui.label_2
        ## set canvas
        self.canvas = QtGui.QPixmap(800, 1200)
        self.canvas.fill(Qt.white)
        # self.ui.label_2.setPixmap(canvas) #创建canvas，并加入label作为画板
        ### canvas settings
        self.max_size = 10
        self.width = 60
        self.height = 30
        self.rect1 = []; self.color1 = []
        self.rect2 = []; self.color2 = []
        self.rect3 = []; self.color3 = []

        self.btn_play = self.ui.pushButton
        self.th = {}
        self.ui.pushButton.clicked.connect(self.run_threads)
        self.ui.pushButton_2.clicked.connect(self.stop_action)
        self.ui.pushButton_3.clicked.connect(self.kill_threads)
   
        
    def video_stop(self):
        self.bClose1 = True
        self.bClose2 = True
    
    def video_start(self):
        self.bClose1 = False
        self.bClose2 = False

    def stop_action(self):
        if self.stop_flag == 0:
            self.stop_flag = 1
        else:
            self.stop_flag = 0
            
    def run_threads(self):
        self.th["video1"] = Thread(target = self.onClick_1, args = (1,))
        self.th["video2"] = Thread(target = self.onClick_2, args = (2,))
        # self.th["canvas"] = Thread(target = self.onClick_2, args = (2,))
        self.th["video1"].start()
        self.th["video2"].start()

    def kill_threads(self):
        if self.bClose1 and self.bClose2:    ### stop
            self.video_start()
            self.th["video1"].join()
            self.th["video2"].join()
            self.video_stop()
        else:
            self.video_stop()

    def onClick_1(self, label): #初始化点击事件
        print("label: ", label)
        if label == 1:
            bClose = self.bClose1
            screen = self.screen1
            video_path = r'oceans.mp4'
        if label == 2:
            bClose = self.bClose2
            screen = self.screen2
            video_path = r'oceans.mp4'
        cap = cv2.VideoCapture(video_path)  #获取视频对象
        fps = cap.get(cv2.CAP_PROP_FPS) 
        if not cap.isOpened():
            print("Cannot open Video File")
            exit()
        num = 0
        ### prepare
        self.Plot()
        # self.ui.label_2.show()
        while not bClose:
            ret, frame = cap.read()  # 逐帧读取影片
            if self.bClose1:
                break
            if not ret:
                if frame is None:
                    print("The video has end.")
                else:
                    print("Read video error!")
                break
            idx = random.randint(1, 4)
            QtImg = cvImgtoQtImg(frame)  # 将帧数据转换为PyQt图像格式
            screen.setPixmap(QtGui.QPixmap.fromImage(QtImg))  # 在ImgDisp显示图像
            size = QtImg.size()
            size = QtCore.QSize(600, 400)
            # print("size: ", size)
            screen.resize(size)  # 根据帧大小调整标签大小
            # self.resize(size)         # 根据帧大小调整窗口大小
            self.btn_play.hide()      # 隐藏播放按钮
            if num % 10 == 0:
                text = self.chooseText(idx)
                self.ui.label.setText(text)
            num += 1
            screen.show()        # 刷新界面
            self.update()
            self.Plot()
            # self.ui.label_2.show()
            while self.stop_flag == 1:#暂停的动作
                cv2.waitKey(int(1000/fps))#休眠一会，因为每秒播放24张图片，相当于放完一张图片后等待41ms
            cv2.waitKey(int(500 / fps))  # 休眠一会，确保每秒播放fps帧

        # 完成所有操作后，释放捕获器
        cap.release()

    def onClick_2(self, label): #初始化点击事件
        print("label: ", label)
        if label == 1:
            bClose = self.bClose1
            screen = self.screen1
            video_path = r'oceans.mp4'
        if label == 2:
            bClose = self.bClose2
            screen = self.screen2
            video_path = r'oceans.mp4'
        cap = cv2.VideoCapture(video_path)  #获取视频对象
        fps = cap.get(cv2.CAP_PROP_FPS) 
        if not cap.isOpened():
            print("Cannot open Video File")
            exit()
        num = 0
        ### prepare
       
        while not bClose:
            ret, frame = cap.read()  # 逐帧读取影片
            if self.bClose2:
                break
            if not ret:
                if frame is None:
                    print("The video has end.")
                else:
                    print("Read video error!")
                break
            idx = random.randint(1, 4)
            QtImg = cvImgtoQtImg(frame)  # 将帧数据转换为PyQt图像格式
            screen.setPixmap(QtGui.QPixmap.fromImage(QtImg))  # 在ImgDisp显示图像
            size = QtImg.size()
            size = QtCore.QSize(600, 400)
            print("size: ", size)
            screen.resize(size)  # 根据帧大小调整标签大小
            # self.resize(size)         # 根据帧大小调整窗口大小
            self.btn_play.hide()      # 隐藏播放按钮
            if num % 10 == 0:
                text = self.chooseText(idx)
                self.ui.label.setText(text)
            num += 1
            screen.show()        # 刷新界面

            while self.stop_flag == 1:#暂停的动作
                cv2.waitKey(int(1000/fps))#休眠一会，因为每秒播放24张图片，相当于放完一张图片后等待41ms
            cv2.waitKey(int(500 / fps))  # 休眠一会，确保每秒播放fps帧

        # 完成所有操作后，释放捕获器
        cap.release()

    def ChooseColor(self, data):
        if data == 0:
            color = QColor(0,225,225)
        if data == 1:
            color = QColor(225,225, 0)
        if data == 2:
            color = QColor(225, 0, 225)
        if data == 3:
            color = QColor(0, 128, 128)
        return color

    def chooseText(self, idx):
        text = ''
        if idx == 1:
            text = "walk forward"
        if idx == 2:
            text = "turn left"
        if idx == 3:
            text = "turn right"
        if idx == 4:
            text == 'sit down'
        return text

    def loadImage(self):
        """ This function will load the camera device, obtain the image
            and set it to label using the setPhoto function
        """
        try:
            faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        except Exception as e:
            print('Warning...',e)
        if self.started:
            self.started=False
            self.pushButton_2.setText('Start')	
        else:
            self.started=True
            self.pushButton_2.setText('Stop')
        
        cam = False # True for webcam
        if cam:
            vid = cv2.VideoCapture(0)
        else:
            vid = cv2.VideoCapture('oceans.mp4')
        
        cnt=0
        frames_to_count=20
        st = 0
        fps=0
        
        while(vid.isOpened()):
            # QtWidgets.QApplication.processEvents()	
            _, image = vid.read()
            image  = imutils.resize(image ,height = 480 )
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
            try:
                faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.15,  
                minNeighbors=7, 
                minSize=(80, 80), 
                flags=cv2.CASCADE_SCALE_IMAGE)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (10, 228,220), 5) 
            except Exception as e:
                pass
            
            if cnt == frames_to_count:
                try: # To avoid divide by 0 we put it in try except
                    print(frames_to_count/(time.time()-st),'FPS') 
                    fps = round(frames_to_count/(time.time()-st)) 
                    st = time.time()
                    cnt=0
                except:
                    pass
            
            cnt+=1
            
            self.update(image,self.label,fps)
            key = cv2.waitKey(1) & 0xFF
            if self.started==False:
                break
                print('Loop break')

    def update(self):
        tdata1 = random.randint(0,3)
        tdata2 = random.randint(0,3)
        tdata3 = random.randint(0,3)
        if self.data1.qsize() > self.max_size:
            print("queue oversize!")
        elif self.data1.qsize() == self.max_size:
            _ = self.data1.get()
        if self.data1.qsize() < self.max_size:
            self.data1.put(tdata1)  ### 插入队尾

        if self.data2.qsize() > self.max_size:
            print("queue oversize!")
        elif self.data2.qsize() == self.max_size:
            _ = self.data2.get()
        if self.data2.qsize() < self.max_size:
            self.data2.put(tdata2)  ### 插入队尾

        if self.data3.qsize() > self.max_size:
            print("queue oversize!")
        elif self.data3.qsize() == self.max_size:
            _ = self.data3.get()
        if self.data3.qsize() < self.max_size:
            self.data3.put(tdata3)  ### 插入队尾

    def DrawRectangle(self, data, color_list, rect_list, pos_x=0, pos_y=500):
        brush = QBrush(Qt.SolidPattern)
        ## move right
        color_list.pop()
        rect_list.pop()
        for i in range(0, self.max_size-1):
            brush.setColor(color_list[i])
            self.painter.setBrush(brush)
            rect = QRect(pos_x+self.width*(i+1), pos_y, self.width, self.height)
            # print("i: ", i)
            self.painter.drawRect(rect)
        ## render new color
        color = self.ChooseColor(data)
        color_list.insert(0, color)
        # print("color: ", color)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(color)
        self.painter.setBrush(brush)
        rect = QRect(pos_x, pos_y, self.width, self.height)
        rect_list.insert(0, rect)
        self.painter.drawRect(rect)

    def Plot(self):
        ### base
        if self.data1.qsize() == 0:
            self.painter_base = QPainter(self.canvas)
            self.painter_base.begin(self)
            self.painter_base.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            for i in range(0, self.max_size):
                brush = QBrush(Qt.SolidPattern)
                brush.setColor(QColor(255,255,255))
                self.painter_base.setBrush(brush)
                rect1 = QRect(0+self.width*i, 530, self.width, self.height)
                rect2 = QRect(0+self.width*i, 580, self.width, self.height)
                rect3 = QRect(0+self.width*i, 630, self.width, self.height)
                # rect.setColor(Qt.blue)
                self.rect1.append(rect1); self.rect2.append(rect2); self.rect3.append(rect3)
                self.color1.append(QColor(255,255,255)); self.color2.append(QColor(255,255,255)); self.color3.append(QColor(255,255,255))
                self.painter_base.drawRect(rect1); self.painter_base.drawRect(rect2); self.painter_base.drawRect(rect3)
            self.painter_base.end()
            self.screen3.setPixmap(self.canvas)
            self.screen3.show()
        else:
            ### dynamic
            self.painter = QPainter(self.canvas)#画图类
            self.painter.begin(self)
            self.painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            data1 = self.data1.queue[-1]
            data2 = self.data2.queue[-1]
            data3 = self.data3.queue[-1]
            print("data1: ", data1)
            self.DrawRectangle(data1, self.color1, self.rect1, 0, 530)
            self.DrawRectangle(data2, self.color2, self.rect2, 0, 580)
            self.DrawRectangle(data3, self.color3, self.rect3, 0, 630)
            # print("data: ", self.data.queue[-1])
            # color = self.ChooseColor(self.data.queue[-1])
            self.painter.end()
            self.screen3.setPixmap(self.canvas)
            self.screen3.show()

class TitleBar(QWidget):

    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.mPos = None
        self.iconSize = 20  # 图标的默认大小
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        # 窗口图标
        self.iconLabel = QLabel(self)
    #         self.iconLabel.setScaledContents(True)
        layout.addWidget(self.iconLabel)
        # 窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setMargin(2)
        layout.addWidget(self.titleLabel)
        # 中间伸缩条
        layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 利用Webdings字体来显示图标
        font = self.font() or QFont()
        font.setFamily('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        layout.addWidget(self.buttonClose)
        # 初始高度
        self.setHeight()

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=38):
        """设置标题栏高度"""
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        # 设置右边按钮的大小
        self.buttonMinimum.setMinimumSize(height, height)
        self.buttonMinimum.setMaximumSize(height, height)
        self.buttonMaximum.setMinimumSize(height, height)
        self.buttonMaximum.setMaximumSize(height, height)
        self.buttonClose.setMinimumSize(height, height)
        self.buttonClose.setMaximumSize(height, height)

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(title)

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(TitleBar, self).enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(TitleBar, self).mouseDoubleClickEvent(event)
        self.showMaximized()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)

class FramelessWindow(QWidget):

    # 四周边距
    Margins = 5

    def __init__(self, *args, **kwargs):
        super(FramelessWindow, self).__init__(*args, **kwargs)

        self._pressed = False
        self.Direction = None
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏边框
        # 鼠标跟踪
        self.setMouseTracking(True)
        # 布局
        layout = QVBoxLayout(self, spacing=0)
        # 预留边界用于实现无边框窗口调整大小
        layout.setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)
        # 标题栏
        self.titleBar = TitleBar(self)
        layout.addWidget(self.titleBar)
        # 信号槽
        self.titleBar.windowMinimumed.connect(self.showMinimized)
        self.titleBar.windowMaximumed.connect(self.showMaximized)
        self.titleBar.windowNormaled.connect(self.showNormal)
        self.titleBar.windowClosed.connect(self.close)
        self.titleBar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        self.windowIconChanged.connect(self.titleBar.setIcon)

    def setTitleBarHeight(self, height=38):
        """设置标题栏高度"""
        self.titleBar.setHeight(height)

    def setIconSize(self, size):
        """设置图标的大小"""
        self.titleBar.setIconSize(size)

    def setWidget(self, widget):
        """设置自己的控件"""
        if hasattr(self, '_widget'):
            return
        self._widget = widget
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self._widget.setAutoFillBackground(True)
        palette = self._widget.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self._widget.setPalette(palette)
        self._widget.installEventFilter(self)
        self.layout().addWidget(self._widget)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super(FramelessWindow, self).move(pos)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super(FramelessWindow, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super(FramelessWindow, self).showNormal()
        self.layout().setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(FramelessWindow, self).eventFilter(obj, event)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super(FramelessWindow, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255, 1), 2 * self.Margins))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super(FramelessWindow, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super(FramelessWindow, self).mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(FramelessWindow, self).mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        wm, hm = self.width() - self.Margins, self.height() - self.Margins
        if self.isMaximized() or self.isFullScreen():
            self.Direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self._resizeWidget(pos)
            return
        if xPos <= self.Margins and yPos <= self.Margins:
            # 左上角
            self.Direction = LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
            # 右下角
            self.Direction = RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos and yPos <= self.Margins:
            # 右上角
            self.Direction = RightTop
            self.setCursor(Qt.SizeBDiagCursor)
        elif xPos <= self.Margins and hm <= yPos:
            # 左下角
            self.Direction = LeftBottom
            self.setCursor(Qt.SizeBDiagCursor)
        elif 0 <= xPos <= self.Margins and self.Margins <= yPos <= hm:
            # 左边
            self.Direction = Left
            self.setCursor(Qt.SizeHorCursor)
        elif wm <= xPos <= self.width() and self.Margins <= yPos <= hm:
            # 右边
            self.Direction = Right
            self.setCursor(Qt.SizeHorCursor)
        elif self.Margins <= xPos <= wm and 0 <= yPos <= self.Margins:
            # 上面
            self.Direction = Top
            self.setCursor(Qt.SizeVerCursor)
        elif self.Margins <= xPos <= wm and hm <= yPos <= self.height():
            # 下面
            self.Direction = Bottom
            self.setCursor(Qt.SizeVerCursor)

    def _resizeWidget(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # myWin = MainWindow()
    # myWin.show()
    # # myWin.showMaximized()
    # sys.exit(app.exec_())
    app = QApplication(sys.argv)
    # app.setStyleSheet(StyleSheet)
    mainWnd = FramelessWindow()
    mainWnd.setWindowTitle('Demo')
    mainWnd.setWindowIcon(QIcon('Qt.ico'))
    mainWnd.resize(QSize(2250,1480))
    mainWnd.setWidget(MainWindow(mainWnd))  # 把自己的窗口添加进来
    mainWnd.show()
    sys.exit(app.exec_())
