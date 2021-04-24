#  Desktop Python Application for using our search engine
# Authors: Ryan Schneider and Josh Singh

import sys
import time
import json
from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * #QIcon
from PyQt5.QtCore import * #Qt, pyqtSlot

# Search Thread
class Worker(QRunnable):
    '''
    Worker Thread

    :param args: Arguments to make available to the run code
    :param kwargs: Keywords arguments to make available to the run code

    '''

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed self.args, self.kwargs
        Execute Query on GenBank and return json object
        '''
        print(self.args, self.kwargs)
        print("Thread start")
        time.sleep(5)
        print("Thread complete")


class mainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__(*args, **kwargs)
        # Initialization Parameters
        self.title = "SaturnLab - GenBank Search Engine"
        self.left = 50
        self.top = 50
        self.width = 600
        self.height = 200
        self.initUI()

        # Initialize Thread Queue
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    # Initialize and constrain the UI
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create the search bar (just a text box)
        # search bar constraints
        tb_x = 20
        tb_y = 20
        tb_w = 280
        tb_h = 40
        self.textbox = QLineEdit(self)
        self.textbox.move(tb_x,tb_y)
        self.textbox.resize(tb_w,tb_h)

        # create search button next to the search bar
        # search button constraints (distance from search bar)
        s_dis = 30
        self.searchButton = QPushButton("Search", self)
        self.searchButton.move(tb_x + tb_w + s_dis, tb_y)
        self.searchButton.clicked.connect(self.search_click)

        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(20,80)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        QMessageBox.question(self, 'Message yah', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        self.textbox.setText("")

    @pyqtSlot()
    def search_click(self):
        # start thread search (send query to worker thread)
        query = self.textbox.text()
        worker = Worker(query)
        self.threadpool.start(worker)
        self.textbox.setText("")

        #QMessageBox.question(self, 'Search', "You searched: " + query, QMessageBox.Ok, QMessageBox.Ok)
        #self.textbox.setText("")


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()