# EC552 Class Project - SaturnSearch

Authors: Cullen Paulisick, Josh Singh, Ryan Schneider, Nikhil Gupta

# Motivation:
The identification and implementation of new synthetic parts within a larger synthetic design is tedious and prone to human error. Foundries need access to robust data infrastructure. 
 
Imagine if researchers always had a ‘TL;DR’ option for automatically scraping synthetic biology parts from existing publications...


# Functionality Overview:
1. Query PMC database based on abstract user input
Ex: “Biosensor design for constitutive production”
2. Latent Dirichlet Allocation model develops topic distribution
Able to more appropriately recommend papers according to parts request
3. Mine relevant papers for parts relevant to topic distribution
IBM-Watson Natural Language Understanding Cloud
4. Display parts, metadata and sequence data in GUI
Make the export of parts data and metadata simple



Project Setup:
1. Create a Python Virtual Environment
2. Use pip to download dependencies from the dependencies.txt : i.e python3 -m pip install -r dependencies.txt
3. run the command : python SaturnSearchAlpha.py
4. Enter the required fields such as API key, server URL, and model ID on the command line when prompted during runtime.


Credits:
Loading animation 'LoadingAnimation.gif' provied by loading.io: www.loading.io

IBM Watson API:
The API key for the Watson has to be dynamically changed so as to avoid security issues from being raised. The login credentials for this application will be sent to graders via email so as to not compromise them. 
The current version of our model can be found at: https://us-south.knowledge-studio.watson.cloud.ibm.com/knowledge-studio/tools/app/rzhz11/tnfm29s18m3g3md1/ui/#/project/2347f980-a858-11eb-ad4d-71f182128617/ml/versions/.
Examples of our training data and model can also be found using these credentials at Deployed model ID will also be provided.

Dependencies:
Package            Version
------------------ ---------
biopython          1.78
certifi            2020.12.5
chardet            4.0.0
click              7.1.2
Cython             0.29.21
gensim             4.0.1
ibm-cloud-sdk-core 3.9.0
ibm-watson         5.1.0
idna               2.10
joblib             1.0.1
json-flatten       0.1
nltk               3.6.2
numpy              1.20.2
pip                21.0.1
PyJWT              2.0.1
PyQt5              5.15.4
PyQt5-Qt5          5.15.2
PyQt5-sip          12.8.1
python-dateutil    2.8.1
python-Levenshtein 0.12.2
regex              2021.4.4
requests           2.25.1
scipy              1.6.2
setuptools         56.0.0
six                1.15.0
smart-open         5.0.0
tqdm               4.60.0
urllib3            1.26.4
websocket-client   0.48.0
wheel              0.36.2
xmltodict          0.12.0

