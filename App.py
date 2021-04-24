#  Desktop Python Application for using our Search Engine
# Authors: Ryan Schneider and Josh Singh

import sys
import traceback
import time
import json
from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * #QIcon
from PyQt5.QtCore import * #Qt, pyqtSlot

# Thread communication signals
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    
    finished = pyqtSignal()
    
    # receives a tuple of Exception type, Exception value and formatted traceback
    error = pyqtSignal(tuple)

    # signal recieving any object type from the executed function
    # in our case this will be a JSON object
    result = pyqtSignal(object)

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
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed self.args, self.kwargs
        Execute Query on GenBank and return json object
        '''
        # Right now, just testing if we can send and recive information from a thread
        print(self.args[0])
        print("Thread start") 
        # query from main
        query = self.args[0] 
        # integrate some querying thing here    

        query_result = "whatever"
        time.sleep(1)
        self.signals.result.emit(query_result)
        print("Thread complete")


class mainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__(*args, **kwargs)
        # Initialization Parameters
        self.title = "SaturnLab - Search Engine"
        self.left = 50
        self.top = 50
        self.width = 1080
        self.height = 720
        self.initUI()

        # Initialize Thread Queue
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    # Initialize and constrain the UI
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # set widget as main window
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # create Layout
        grid = QGridLayout()
        wid.setLayout(grid)

        # create the search bar (just a text box)
        # search bar constraints
        tb_x = 20
        tb_y = 20
        tb_w = 280
        tb_h = 40
        self.textbox = QLineEdit(self)
        self.textbox.resize(tb_w,tb_h)
        grid.addWidget(self.textbox, 0,0)

        # create search button next to the search bar
        # search button constraints (distance from search bar)
        s_dis = 30
        self.searchButton = QPushButton("Search", self)
        #self.searchButton.move(tb_x + tb_w + s_dis, tb_y)
        self.searchButton.clicked.connect(self.search_click)
        grid.addWidget(self.searchButton, 0,1)

        # Create a button in the window
        self.button = QPushButton('Show text', self)
        #self.button.move(20,80)
        grid.addWidget(self.button, 1,0)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        

        # make list view below search bar
        # search results constraints
        sr_dis = 120
        sr_w = 100
        sr_h = 100
        self.searchResults = QListWidget(self)
        #self.searchResults.move(tb_x, tb_y + tb_h + sr_dis)
        self.searchResults.insertItem(0, "Best Paper Ever")
        grid.addWidget(self.searchResults, 2,0)
        self.searchResults.resize(sr_w,sr_h)

        # make a large label to the write of the list view
        self.paperView = QLabel("test", self)
        grid.addWidget(self.paperView, 2,2)

        self.show()
    
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        QMessageBox.question(self, 'Message yah', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        self.textbox.setText("")


    # Don't need slots for local main functions that are called
    # populate list view
    def display_results(self, results):
        QMessageBox.question(self, 'Search Results', "From Thread: " + results, QMessageBox.Ok, QMessageBox.Ok)
        # loop and print json dictionary
        


    @pyqtSlot()
    def search_click(self):
        # start thread search (send query to worker thread)
        query = self.textbox.text()
        worker = Worker(query)
        # connect signals in worker to functions in main
        worker.signals.result.connect(self.display_results)

        # connect worker
        self.threadpool.start(worker)
        self.textbox.setText("")

        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
