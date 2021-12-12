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

        self.createMatplot()
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


    def getDataAligned(self):
        self.dates=[]
        self.count_good=[]
        self.count_bad=[]
        k=0
        for i in self.alldata:
            time= i[3].strftime("%H:%M")

            if(i[3] not in  self.dates):
                self.dates.append(i[3])
                k=len(self.dates)-1
                self.count_good.append([])
                self.count_bad.append([])

            if(i[2]=="Good"):
                self.count_good[k].append("Good")
            else:
                self.count_bad[k].append("Bad")



    def createMatplot(self):
        diff=6000
        self.getDataAligned()
        xpoints = np.array(self.dates,dtype='datetime64[D]')
        #np.array([ self.alldata[i*diff][3].strftime("%H:%M") for i in range(4)] )

        ypoints = np.array([len(i) for i in self.count_good])
        ypoints1 = np.array([len(i) for i in self.count_bad])
        #fig = plt.plot(xpoints, ypoints)
        print(xpoints)
        print(ypoints)
        print(ypoints1)
        # plot
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__

        self.canvas = FigureCanvas(self.figure)



        self.figure.gca().bar(xpoints, ypoints,color='g')
        self.figure.gca().bar(xpoints, ypoints1,bottom=ypoints, color='y')


        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method


    def setGalleryTab(self):
        self.tab2.layout = QGridLayout(self)
        pics = [
                "1.png",
                "2.png",
                "1.png",
                "2.png",
                ]*4
        print(pics)
        self.populate(pics, QSize(64,64))
        self.tab2.setLayout(self.tab2.layout)


    def populate(self, pics, size, imagesPerRow=4,
                 flags=Qt.KeepAspectRatioByExpanding):
        row = col = 0
        for pic in pics:
            label = ImageLabel("")
            pixmap = QPixmap(pic)
            pixmap = pixmap.scaled(size, flags)
            label.setPixmap(pixmap)
            self.tab2.layout.addWidget(label, row, col)
            col += 1
            if col % imagesPerRow == 0:
                row += 1
                col = 0






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