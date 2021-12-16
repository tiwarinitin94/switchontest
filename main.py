import sys
from PyQt5.QtWidgets import *


from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib
import matplotlib.pylab as plt
from matplotlib.figure import Figure
import random
import datetime
import mysql.connector

matplotlib.use('qt5agg')

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas,     NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class DataConnection():
    def __init__(self, parent=None):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="switchon_test"
        )
        self.mycursor = self.mydb.cursor()

    def insertData(self, table_name, columns, data):
        sql = "INSERT INTO "+table_name+" ("+columns+") VALUES ("+data+")"
        self.mycursor.execute(sql)
        self.mydb.commit()

    def generateData(self):
        date_data=datetime.datetime.today()
        k=0
        for i in range(24000):
            k=k+1
            status = random.choice(["Good", "Bad"])
            if k==6000:
                date_data = date_data + datetime.timedelta(minutes=30)
                k=0

            dateval = date_data.strftime('%Y-%m-%d %H:%M:%S')

            self.insertData('sku_db',"skuid,status,time_stamp","'skuid"+str(i)+"' , '"+status+"','"+dateval+"' ",)

    def getCountData(self, table_name):
        sql = "SELECT count(*) FROM " + table_name
        count = self.mycursor.execute(sql)

        fixture_count = self.mycursor.fetchone()[0]
        return fixture_count

    def getAllData(self,table_name):
        sql = "SELECT * FROM "+table_name
        self.mycursor.execute(sql)

        return self.mycursor.fetchall()

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        connect_data = DataConnection()
        count=connect_data.getCountData('sku_db')
        if(count==0):
            connect_data.generateData()


        self.setGeometry(300,100,1000,500)
        self.setWindowTitle("My Window")
        self.initUI()


    def initUI(self):
        self.tab_widget = MyTabWidget(self)
        self.setCentralWidget(self.tab_widget)


class MyTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout =QFormLayout(self)
        #QVBoxLayout(self)
        self.connect_data = DataConnection()
        self.alldata = np.array([list(i) for i in self.connect_data.getAllData('sku_db')])


        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tab2_defult=1 #for showing all data

        self.tabs.resize(900, 900)

        # Add tabs
        self.tabs.addTab(self.tab1, "Analytics")
        self.tabs.addTab(self.tab2, "Image Gallery")

        self.setAnalyticsTab()

        self.setGalleryTab()



        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


    def setAnalyticsTab(self):
        # Create first tab
        self.tab1.layout = QFormLayout(self)
        # QGridLayout(self)

        self.addDropDown()

        self.createMatplot([],[],[])
        # self.tab1.layout.addWidget(self.l,0,0)
        self.tab1.layout.addRow(self.dropdown)

        #self.tab1.layout.addRow(self.toolbar)
        self.tab1.layout.addRow(self.canvas)

        # self.button = QtGui.QPushButton('Inspection start')
        # self.button.clicked.connect(self.genrateDataAnalytic)
        # self.tab1.layout.addRow(self.button)


        self.tab1.setLayout(self.tab1.layout)

    def genrateDataAnalytic(self):
        self.connect_data.generateData()


    def addDropDown(self):
        self.dropdown= QComboBox(self)
        self.dropdown.setGeometry(10,10,20,10)
        self.dropdown.addItem("Please select SKU")
        self.dropdown.addItem("SKU Selection")
        self.dropdown.currentIndexChanged.connect(self.dropDownChange)

    def dropDownChange(self,i):
        print(self.dropdown.currentText())
        self.canvas.setParent(None)
        self.getDataAligned()
        xpoints = np.array(self.dates)
        ypoints = np.array([len(i) for i in self.count_good])
        ypoints1 = np.array([len(i) for i in self.count_bad])
        self.createMatplot(xpoints,ypoints,ypoints1)
        self.tab1.layout.addRow(self.canvas)




    def getDataAligned(self):
        self.dates=[]
        self.count_good=[]
        self.count_bad=[]
        k=0
        for i in self.alldata:

            if(i[3].strftime("%H:%M") not in  self.dates):
                self.dates.append(i[3].strftime("%H:%M"))
                k=len(self.dates)-1
                self.count_good.append([])
                self.count_bad.append([])

            if(i[2]=="Good"):
                self.count_good[k].append("Good")
            else:
                self.count_bad[k].append("Bad")



    def createMatplot(self,xpoints,ypoints,ypoints1):

        # plot
        self.figure = Figure()



        self.canvas = FigureCanvas(self.figure)

        self.figure.gca().bar(xpoints, ypoints,color='g',label="Good")
        self.figure.gca().bar(xpoints, ypoints1,bottom=ypoints, color='r',label="Bad")




    def setGalleryTab(self):
        self.vboxlayout = QVBoxLayout(self)
        self.tab2.layout = QGridLayout(self)

        pics = [
                "1.png", #Good
                "2.png", #Bad
                ]
        self.vLayout = QHBoxLayout(self)

        self.populate(pics, QSize(64,64),1)





        #self.tab2.setLayout(vLayout)
        self.setTab2Data()



    def setTab2Data(self):
        pics = [
            "1.png",  # Good
            "2.png",  # Bad
        ]
        for i in reversed(range(self.vboxlayout.count())):
            if self.vboxlayout.itemAt(i).widget() is not None:
                self.vboxlayout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.vLayout.count())):
            if self.vLayout.itemAt(i).widget() is not None:
                self.vLayout.itemAt(i).widget().setParent(None)

        self.vLayout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        btn1 = QtWidgets.QPushButton('All')
        # vLayout.addWidget(btn1, alignment=QtCore.Qt.AlignRight)

        btn2 = QtWidgets.QPushButton('Good')
        # vLayout.addWidget(btn2, alignment=QtCore.Qt.AlignRight)

        btn3 = QtWidgets.QPushButton('Bad')
        # vLayout.addWidget(btn3, alignment=QtCore.Qt.AlignRight)

        self.vLayout.addWidget(btn1)
        self.vLayout.addWidget(btn2)
        self.vLayout.addWidget(btn3)

        btn1.clicked.connect(lambda: self.populate(pics, QSize(64, 64), 1))
        btn2.clicked.connect(lambda: self.populate(pics, QSize(64, 64), 2))
        btn3.clicked.connect(lambda: self.populate(pics, QSize(64, 64), 3))
        self.vboxlayout.addLayout(self.vLayout)
        self.vboxlayout.addLayout(self.tab2.layout)
        self.tab2.setLayout(self.vboxlayout)

    def populate(self, pics, size,data_type, imagesPerRow=6,
                 flags=Qt.KeepAspectRatioByExpanding):
        row = col = 0
        print(data_type)

        self.tab2.layout.setParent(None)
        for i in reversed(range(self.tab2.layout.count())):
            if self.tab2.layout.itemAt(i).widget() is not None:
                self.tab2.layout.itemAt(i).widget().setParent(None)

        self.tab2.layout = QGridLayout(self)
        count=0
        for i in self.alldata:
            print(i[2])
            if (i[2] == "Good") and (data_type == 2):
                label = ImageLabel("Good")
                pixmap = QPixmap(pics[0])
                pixmap = pixmap.scaled(size, flags)
                label.setPixmap(pixmap)
                print("Good"+str(data_type))
                count+=1
            elif (i[2] == "Bad") and (data_type== 3):
                label = ImageLabel("Bad")
                pixmap = QPixmap(pics[1])
                pixmap = pixmap.scaled(size, flags)
                label.setPixmap(pixmap)
                print("Bad")
                count += 1
            else:
                if (i[2] == "Bad") :
                    label = ImageLabel("Bad")
                    pixmap = QPixmap(pics[0])
                    pixmap = pixmap.scaled(size, flags)
                    label.setPixmap(pixmap)
                    print("Bad"+str(data_type)+ i[2])
                    count += 1
                else:
                    label = ImageLabel("Good")
                    pixmap = QPixmap(pics[1])
                    pixmap = pixmap.scaled(size, flags)
                    label.setPixmap(pixmap)
                    print("Good")
                    count += 1


            self.tab2.layout.addWidget(label, row, col)
            col += 1
            if count==60:
                break
            if col % imagesPerRow == 0:
                row += 1
                col = 0
        self.setTab2Data()





class ImageGallery(QDialog):

    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.setWindowTitle("Image Gallery")
        self.setLayout(QGridLayout(self))



class ImagePopup(QLabel):
    """
    The ImagePopup class is a QLabel that displays a popup, zoomed image
    on top of another label.
    """

    def __init__(self, parent):
        super(QLabel, self).__init__(parent)

        thumb = parent.pixmap()
        imageSize = thumb.size()
        imageSize.setWidth(imageSize.width() * 2)
        imageSize.setHeight(imageSize.height() * 2)
        self.setPixmap(thumb.scaled(imageSize, Qt.KeepAspectRatioByExpanding))

        # center the zoomed image on the thumb
        position = self.cursor().pos()
        position.setX(position.x() - thumb.size().width())
        position.setY(position.y() - thumb.size().height())
        self.move(position)

        # FramelessWindowHint may not work on some window managers on Linux
        # so I force also the flag X11BypassWindowManagerHint
        self.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint
                            | Qt.FramelessWindowHint
                            | Qt.X11BypassWindowManagerHint)

    def leaveEvent(self, event):
        """ When the mouse leave this widget, destroy it. """
        self.destroy()


class ImageLabel(QLabel):
    """ This widget displays an ImagePopup when the mouse enter its region """

    def enterEvent(self, event):
        self.p = ImagePopup(self)
        self.p.show()
        event.accept()





# class UIcomponents(QT)

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    main = MainWindow()
    main.show()
    # Run the main Qt loop
    sys.exit(app.exec())