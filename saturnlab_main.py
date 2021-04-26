# this is a script for retrieving user input and displaying results of genetic sequences
from gensim.models import LdaModel
import pprint
from saturnlab_textprep import bow_corpus, bow_string,search
import os
from os import path
import json
import xmltodict
import requests
import xml.etree.ElementTree as ET
import xmltodict
from json_flatten import flatten

"""
Recieve input from user and map search terms to LDA topic distribution.
This script first recieves input from the user and then maps these string to the exisiting model. 
The map of this user input is then matched with the maps of connected papers. The papers are ranked in order of relavence to 
the search term by taking the dot product of the user input map with the map of the respective papers.
The papers with the highest dot product are recommended and displayed, along with their parts (courtesy of IBM).
"""
# change path to model and import
os.chdir('/Users/cullenpaulisick/Documents/EC552/Project/EC552SaturnLab/Models/Modelv2')
lda = LdaModel.load('modelv2.gensim')

# change working directory back to main script
scriptpath = os.path.abspath(__file__)
dname = os.path.dirname(scriptpath)
os.chdir(dname)

# get user input
input_text = input("Search Terms: ")
user_terms_corpus = bow_string(input_text)
# create user map
user_map = lda[user_terms_corpus[0]]
print(user_map)
# extract relevant papers from pmc
papers_results = search(input_text)
paper_Ids = papers_results['IdList']
print("Recieving text data from NCBI...")
# recieve full text from web
payload = {'db':'pmc', 'id':paper_Ids}
response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=payload)
string_xml = response.text
tree = ET.fromstring(string_xml)
xml_str = ET.tostring(tree, method='xml')
text_data = (xmltodict.parse(xml_str))

# create text corpus from raw text data
kwds = {}
original_corpus = {}
print("Creating dataset from text data...")
# code to convert ini_dict to flattened dictionary
print(text_data.keys())
for i, paper in enumerate(text_data['pmc-articleset']['article']):
    try:
        pmid = paper['front']['article-meta']['article-id'][0]["#text"]
        flat_data = flatten(paper['body'])
        # apply filter for any value over 10 characters in length
        text_res = dict((key, flat_data[key]) for key in flat_data.keys() if (len(flat_data[key]) > 30) and ('{' not in flat_data[key]))
        concat_text = " ".join(list(text_res.values())) + "."
        concat_text = concat_text.replace("[]", "").replace("[,]", "")
        original_corpus[pmid] = concat_text
        kwds[pmid] = paper['front']['article-meta']['kwd-group']['kwd']
    except:
        pass

# create bag-of-words representation for corpus 
corpus_texts = list(original_corpus.values())
print(len(corpus_texts))
bag_of_words = bow_corpus(corpus_texts)
bag_of_words_corpus = bag_of_words[0]
print(len(bag_of_words_corpus))
dictionary = bag_of_words[1]
# create LDA mapping for papers returned from search
paper_mapping = {}
for i, text in enumerate(bag_of_words_corpus):
    paper_mapping[list(original_corpus.keys())[i]] = lda[text]

# for key, value in paper_mapping.items():
#     print(key)
#     print(value)
for keys, values in paper_mapping.items():
    













