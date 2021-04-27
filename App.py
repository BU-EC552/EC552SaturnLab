#  Desktop Python Application for using our Search Engine
# Authors: Ryan Schneider and Josh Singh

# Application for retrieving user input and displaying results of genetic sequences
import saturnlab_main as ex
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
import os
import os.path

from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * #QIcon
from PyQt5.QtCore import * #Qt, pyqtSlot

results_text = 0
global_gene_list = 0

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
        #query_result = user_search(query)
        query_result = ex.saturnlab_extract(query)
        time.sleep(5)
        self.signals.result.emit(query_result)

        print("Thread complete")


class mainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__(*args, **kwargs)
        # Initialization Parameters
        self.title = "SaturnSearch - Search Engine"
        self.left = 50
        self.top = 50
        self.width = 1600
        self.height = 900
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
        self.SearchBar.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
        self.SearchBar.resize(300,300)

        self.mainGrid.addWidget(self.SearchBar, 2,1)

        # create search button
        self.mainSearchButton = QPushButton("Search")
        self.mainSearchButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
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
        self.textbox.setStyleSheet("*{border-radius: 5px; height: 75px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
  
        self.grid.addWidget(self.textbox, 0,0)

        # create search button next to the search bar
        # search button constraints (distance from search bar)
        s_dis = 30
        self.searchButton = QPushButton("Search", self)
        #self.searchButton.move(tb_x + tb_w + s_dis, tb_y)
        self.searchButton.clicked.connect(self.search_click)
        self.grid.addWidget(self.searchButton, 0,1)
        self.searchButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")

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
        self.searchResults.setStyleSheet(":item{font-size: 25px; font-weight: bold; height: 200px; border: 1px solid black; border-radius: 30px} :item:hover{border: 2px solid blue} :item:selected{background-color: #029D9C}")
        #self.searchResults.move(tb_x, tb_y + tb_h + sr_dis)
        self.searchResults.itemClicked.connect(self.result_click)
        self.twoBox.addWidget(self.searchResults)
        self.searchResults.resize(sr_w,sr_h)

        # make a large label to the write of the list view
        # make button underneath that lets us see genbank sequences
        self.paper_widget = QWidget()
        vert_layout = QVBoxLayout()
        

        self.paperView = QLabel("", self)
        self.paperView.setStyleSheet("*{border: 1px solid black;}")
        self.paperView.resize = (400, sr_h)
        vert_layout.addWidget(self.paperView)
        self.twoBox.addWidget(self.paper_widget)

        # qlistwidget of parts
        self.genList = QListWidget()
        self.genList.setStyleSheet(":item{font-size: 25px; font-weight: bold; height: 75px; border: 1px solid black; border-radius: 30px} :item:hover{border: 2px solid blue} :item:selected{background-color: #029D9C}")
        self.genList.resize(50,50)
        self.genList.itemClicked.connect(self.open_dialog)
        vert_layout.addWidget(self.genList)

        # make a label to display the loading animation
        # make label to hold layout for centring
        self.help_animate = QWidget()
        horizontalGrid = QHBoxLayout()
        
        self.animateLabel = QLabel(None,self)
        #self.animateLabel2 = QLabel(None, self)
        # loading animation
        self.movie = QMovie("LoadingAnimation.gif")
        #self.movie2 = QMovie("LoadingAnimation.gif")
        self.animateLabel.setMovie(self.movie)
        self.animateLabel.setStyleSheet(*{"height: 300px; width: 400px "})
        #self.animateLabel2.setMovie(self.movie2)

        horizontalGrid.addStretch()
        horizontalGrid.addWidget(self.animateLabel)
        #horizontalGrid.addWidget(self.animateLabel2)
        horizontalGrid.addStretch()
        self.help_animate.setLayout(horizontalGrid)
        self.paper_widget.setLayout(vert_layout)
        self.sr_stack.addWidget(self.help_animate)
        self.sr_stack.addWidget(self.lowerHalfWidget)
        self.sr_stack.setCurrentIndex(0)

        self.show()

    #@pyqtSlot()
    #def on_click(self):
    #    textboxValue = self.textbox.text()
    #    QMessageBox.question(self, 'Message yah', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
    #    self.textbox.setText("")

    #@pyqtSlot()
    #def mouseEnterSearch(self, Object):
    #    self.textbox.setText("Nice")

    #@pyqtSlot()
    #def mouseLeaveSearch(self, Object):
    #    self.textbox.setText("")

    # start loading animation
    def start_loading(self):
        self.movie.start()
        #self.movie2.start()

    # stop loading animation
    def stop_loading(self):
        self.movie.stop()
        #self.movie2.stop()

    
    @pyqtSlot()
    def result_click(self):
        global global_gene_list
        self.genList.clear()
        text_results = self.searchResults.currentItem().text()
        parse = text_results.split("PMID:")
        pmid = parse[1]
        print(pmid)
        # display entity response data
        global results_text
        r = results_text
        parts_list = []
        gene_list = []
        sequence_list = []
        for part in r[2][pmid]['entities']:
            if part['type'].lower() == 'part':
                if part['text'] not in parts_list:
                    parts_list.append(part['text'])
                    if part['disambiguation']['subtype'][0].lower() != 'none' and part['disambiguation']['subtype'][0].lower() != 'sequence':
                        gene_list.append(part['text'])
                    if part['disambiguation']['subtype'][0].lower() == 'sequence':
                        sequence_list.append(part['text'])
        
        # update list
        print(parts_list)
        print(gene_list)
        print(sequence_list)
        for i in parts_list: 
            new_item = QListWidgetItem()
            output_text = i
            if i in gene_list:
                output_text = output_text + " @Gene"
            new_item.setText(output_text)
            self.genList.addItem(new_item)

        # update gene list
        output_seq = "Parts in Paper: "
        for i in sequence_list:
            output_seq = output_seq + i + " \n"
        self.paperView.setText(output_seq)

        global_gene_list = gene_list


    # opened window for parts (that are genes)
    def open_dialog(self):
        dlg = QDialog()
        dlg.setWindowTitle("Export Window")
        dlg.layout = QVBoxLayout()

        dlg.btn1 = QPushButton("Export GenBank")
        dlg.btn1.clicked.connect(self.genbank_export)
        dlg.layout.addWidget(dlg.btn1)

        dlg.btn2 = QPushButton("Export JSON File")
        dlg.btn2.clicked.connect(self.json_export)
        dlg.layout.addWidget(dlg.btn2)
        
        dlg.setLayout(dlg.layout)
        dlg.exec()

    
    def genbank_export(self):
        global results_text
        global global_gene_list
        text_results = self.genList.currentItem().text()
        parse = text_results.split("@")
        print(parse)
        if len(parse) > 1:
            gene = parse[0]
            Entrez.email = 'clp0216@bu.edu'
            handle = Entrez.esearch(db='nucleotide',
            sort='relevance',
            retmax='810',
            retmode='text',
            term=gene+'[gene]',
            idtype='acc'
            )
            ncbi_res = Entrez.read(handle)
            res_IdList = ncbi_res['IdList']
            handle_set = []
            for acc_num in res_IdList[:3]:
                fetch_handle = Entrez.efetch(db='nucleotide',
                id=acc_num,
                rettype="gb",
                retmode="text")
                data = fetch_handle.read()
                handle_set.append(data)
            
            new_dir = "genBank_output_" + gene
            #os.chdir(new_dir)
            for i, textfile in enumerate(handle_set):
                with open("gb_" + str(i) + ".txt", 'w') as f:
                    f.write(textfile)
                f.close()
            #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        else:
            print("Not a gene!")    

    def json_export(self):
        global results_text
        r = results_text
        text_results = self.searchResults.currentItem().text()
        parse = text_results.split("PMID:")
        pmid = parse[1]
        print(pmid)
        entities = r[2]
        dict_output = entities[pmid]
        json_file = json.dumps(dict_output, indent=2)
        #new_dir = "json_output_" + pmid
        #os.mkdir(new_dir)
        #os.chdir(new_dir)
        with open("json_" + pmid + ".json", 'w') as f:
            f.write(json_file)
        f.close()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))



    # Don't need slots for local main functions that are called
    # populate list view
    def display_results(self, r):
        # stop animation and change view 
        self.searchButton.setEnabled(True)
        self.stop_loading()
        self.sr_stack.setCurrentIndex(1)
        global results_text
        results_text = r

        # 0 , Paper rankings
        # 1 , stub (names and authors)
        # 2 , entity_response  (parts and methods found in papers)
        # 3 , concept_response (broad concepts in papers)
        #print(r[0])
        # loop and print json dictionary
        count = 0
        for pmid, val in r[0].items():
            #print(r[1][pmid])
            # pmid is paper index in stubs
            new_item = QListWidgetItem()
            text = r[1][pmid]
            parse = text.split('*')
            new_item.setText(parse[0] + "." + "\n\n Authors: " + parse[1] + "\n\n Relevance Score: " + str(val * 100) + "\n" + "PMID:" + pmid )
            #new_item.enterEvent = self.result_hover(pmid)
            #new_item.clicked.connect(self.result_click(self))
            self.searchResults.addItem(new_item)
            count = count + 1
           
    

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
        self.searchButton.setEnabled(False)

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

        # disable search button while searching
        self.searchButton.setEnabled(False)

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
