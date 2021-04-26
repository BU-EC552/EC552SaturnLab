#  Desktop Python Application for using our Search Engine
# Authors: Ryan Schneider and Josh Singh

# Application for retrieving user input and displaying results of genetic sequences
from Bio import Entrez
from gensim.models import LdaModel
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
import pprint
import sys
import traceback
import time
import json

from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * #QIcon
from PyQt5.QtCore import * #Qt, pyqtSlot

class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(200, 200)

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
    result = pyqtSignal(object,object)

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
        # integrate results with pubmed (query using user input from search box)
        query = self.args[0]
        #query_result = user_search(query)
        query_result0 = query + "test0"
        query_result1 = query + "test1"
        time.sleep(5)
        self.signals.result.emit(query_result0, query_result1)

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
        self.initMainScreenUI()
        self.initCompareUI()

        # Initialize Thread Queue
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def initMainScreenUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # set widget as main window
        self.wid = QWidget()
        self.setCentralWidget(self.wid)

        # create stacked layout
        self.stack = QStackedLayout()
        self.wid.setLayout(self.stack)

        # create grid layout
        self.mainGrid = QGridLayout()
        self.enterWidget = QWidget()
        self.enterWidget.setLayout(self.mainGrid)
        self.stack.addWidget(self.enterWidget)
        self.stack.setCurrentIndex(0)

        self.SearchBar = QLineEdit(self)
        self.SearchBar.resize(300,300)

        self.mainGrid.addWidget(self.SearchBar, 2,1)

        # create search button
        self.mainSearchButton = QPushButton("Search")
        self.mainGrid.addWidget(self.mainSearchButton, 2,2)
        self.mainSearchButton.clicked.connect(self.mainSearch_click)

    # Initialize and constrain the UI
    def initCompareUI(self):
        # define main widget
        self.compareWidget = QWidget()
        self.grid = QGridLayout()
        self.compareWidget.setLayout(self.grid)
        self.stack.addWidget(self.compareWidget)

        # create the search bar (just a text box)
        # search bar constraints
        tb_x = 20
        tb_y = 20
        tb_w = 280
        tb_h = 40
        self.textbox = QLineEdit(self)
        self.textbox.resize(tb_w,tb_h)
        # install event filter
        #self.textbox.enterEvent = self.mouseEnterSearch
        #self.textbox.leaveEvent = self.mouseLeaveSearch
        #self.textbox.setStyleSheet("border-radius: 5px")
        self.textbox.setStyleSheet(":hover {border: 2px solid #006080}")
  
        self.grid.addWidget(self.textbox, 0,0)

        # create search button next to the search bar
        # search button constraints (distance from search bar)
        s_dis = 30
        self.searchButton = QPushButton("Search", self)
        #self.searchButton.move(tb_x + tb_w + s_dis, tb_y)
        self.searchButton.clicked.connect(self.search_click)
        self.grid.addWidget(self.searchButton, 0,1)
        self.searchButton.setStyleSheet(":hover {background-color: black}")

        # Create a button in the window
        #self.button = QPushButton('Show text', self)
        #self.button.move(20,80)
        #grid.addWidget(self.button, 1,0)
        
        # connect button to function on_click
        #self.button.clicked.connect(self.on_click)
        

        # make list view below search bar
        # the search results and the loading animation are going to populate a stacked layout
        self.resultWidget = QWidget()
        self.sr_stack = QStackedLayout()
        self.resultWidget.setLayout(self.sr_stack)
        self.grid.addWidget(self.resultWidget,1,0)
        
        # create lower half screen with two windows
        self.lowerHalfWidget = QWidget()
        self.twoBox = QHBoxLayout()
        self.lowerHalfWidget.setLayout(self.twoBox)
        
        # search results constraints
        sr_dis = 120
        sr_w = 100
        sr_h = 100
        self.searchResults = QListWidget(self)
        #self.searchResults.move(tb_x, tb_y + tb_h + sr_dis)
        self.searchResults.insertItem(0, "Best Paper Ever")
        self.twoBox.addWidget(self.searchResults)
        self.searchResults.resize(sr_w,sr_h)

        # make a large label to the write of the list view
        self.paperView = QLabel("Display Paper", self)
        #self.paperView.resize = (sr_w * 2, sr_h * 2)
        self.twoBox.addWidget(self.paperView)

        # make a label to display the loading animation
        self.animateLabel = QLabel(None,self)
        # loading animation
        self.movie = QMovie("LoadingAnimation.gif")
        self.animateLabel.setMovie(self.movie)

        self.sr_stack.addWidget(self.animateLabel)
        self.sr_stack.addWidget(self.lowerHalfWidget)
        self.sr_stack.setCurrentIndex(0)

        self.show()

    #@pyqtSlot()
    #def on_click(self):
    #    textboxValue = self.textbox.text()
    #    QMessageBox.question(self, 'Message yah', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
    #    self.textbox.setText("")

    @pyqtSlot()
    def mouseEnterSearch(self, Object):
        self.textbox.setText("Nice")

    @pyqtSlot()
    def mouseLeaveSearch(self, Object):
        self.textbox.setText("")

    # start loading animation
    def start_loading(self):
        self.movie.start()

    # stop loading animation
    def stop_loading(self):
        self.movie.stop()

    # Don't need slots for local main functions that are called
    # populate list view
    def display_results(self, r1, r2):
        # stop animation and change view 
        self.stop_loading()
        self.sr_stack.setCurrentIndex(1)
        print(r1)
        print(r2)
        # loop and print json dictionary



    @pyqtSlot()
    def search_click(self):
        # start thread search (send query to worker thread)
        self.sr_stack.setCurrentIndex(0)
        self.start_loading()
        query = self.textbox.text()
        worker = Worker(query)
        # connect signals in worker to display_result function in main
        worker.signals.result.connect(self.display_results)
        self.start_loading()

        # connect worker
        self.threadpool.start(worker)
        self.textbox.setText("")

    @pyqtSlot()
    def mainSearch_click(self):
        # start thread search (send query to worker thread)
        query = self.SearchBar.text()
        worker = Worker(query)
        # connect result emit signal in worker to display_result function in main
        worker.signals.result.connect(self.display_results)
        # start thread
        self.threadpool.start(worker)
        # change index of stacked layout
        self.stack.setCurrentIndex(1)

        # set nested stack to movie stack index
        self.sr_stack.setCurrentIndex(0)

        # start animation
        self.start_loading()

        # copy text to internal search bar
        self.textbox.setText(query)

        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
