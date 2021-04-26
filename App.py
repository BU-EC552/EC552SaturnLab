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

def bow_corpus(original_corpus):
    docs = list(original_corpus)
    # Tokenize the documents.
    
    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 2] for doc in docs]

    # Lemmatize the documents.

    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]
    
    # Compute bigrams.
    from gensim.models import Phrases

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    bigram = Phrases(docs, min_count=20)
    for idx in range(len(docs)):
        for token in bigram[docs[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                docs[idx].append(token)

    # Remove rare and common tokens.
    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    print(docs[0])
    # Bag-of-words representation of the documents.
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    return corpus, dictionary

def bow_string(doc):
    from nltk.tokenize import RegexpTokenizer
    from nltk.corpus import stopwords
    from gensim.corpora import Dictionary
    import numpy as np
    doc = doc.lower()
    # tokenize string
    tokenizer = RegexpTokenizer(r'\w+')
    doc = doc.lower()  # Convert to lowercase.
    doc = tokenizer.tokenize(doc)  # Split into words.
    # remove stopwords
    stop_words = stopwords.words('english')
    user_terms = [token for token in doc if token not in stop_words]
    # convert terms into word-order agnostic 2D list
    print(user_terms)
    user_array = np.array(user_terms)
    user_corpus = [np.roll(user_array, i) for i in range(len(user_terms))]
    user_corpus = [list(arr) for arr in user_corpus]
    print(user_corpus)
    # create dictionary and bag-of-words
    dictionary = Dictionary(user_corpus)
    text_corpus = [dictionary.doc2bow(doc) for doc in user_corpus]
    return text_corpus

    # Pass user string input as search term to LDA model
def user_search(input_text):
    lda = LdaModel.load('Models/Model0/model1.gensim')
    user_terms_corpus = bow_string(input_text)
    return lda.print_topics(num_words=5)


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
        # integrate results with pubmed (query using user input from search box)
        query = self.args[0]
        query_result = user_search(query)
        
        time.sleep(5)
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
        self.textbox.enterEvent = self.mouseEnterSearch
        self.textbox.leaveEvent = self.mouseLeaveSearch
        self.textbox.setStyleSheet(":hover {border: 2px solid #006080}")
        #self.textbox.setStyleSheet("{border-image: url(:/testSearch-trimmy.png)}")
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
        # the search results and the loading animation are going to populate a stacked layour
        #self.sr_stack = QStackedLayout()
        #self.grid.addWidget(self.sr_stack)
        # search results constraints
        sr_dis = 120
        sr_w = 100
        sr_h = 100
        self.searchResults = QListWidget(self)
        #self.searchResults.move(tb_x, tb_y + tb_h + sr_dis)
        self.searchResults.insertItem(0, "Best Paper Ever")
        self.grid.addWidget(self.searchResults, 2,0)
        self.searchResults.resize(sr_w,sr_h)

        # make a large label to the write of the list view
        self.paperView = QLabel("Display Paper", self)
        self.paperView.resize = (sr_w * 2, sr_h * 2);
        self.grid.addWidget(self.paperView, 2,2)

        # make a label to display the loading animation
        self.animateLabel = QLabel(None, self);
        self.grid.addWidget(self.animateLabel, 2,1)

        # loading animation
        self.movie = QMovie("LoadingAnimation.gif")
        self.animateLabel.setMovie(self.movie)


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
    def display_results(self, results):
        QMessageBox.question(self, 'Search Results', "From Thread: " + str(results), QMessageBox.Ok, QMessageBox.Ok)
        # loop and print json dictionary


    @pyqtSlot()
    def search_click(self):
        # start thread search (send query to worker thread)
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

        # change index of nested stacked layout
        
        # start animation
        self.start_loading()

        # copy text to internal search bar
        self.textbox.setText(query)

        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
