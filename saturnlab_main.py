# this is a script for retrieving user input and displaying results of genetic sequences
from gensim.models import LdaModel
import pprint
from saturnlab_textprep import bow_corpus, bow_string,search, parts_prep
import os
from os import path
import json
import xmltodict
import requests
import xml.etree.ElementTree as ET
import xmltodict
from json_flatten import flatten
import numpy as np
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, ConceptsOptions


def saturnlab_extract(input_text):

    """
    The parts extraction feature uses a base model from IBM Watson NLU service. In order to use this service, 
    authentication is required. Credentials are provided below.
    """
    # api key
    api_key = 'icmDJw0O-dSqYOoEcKwt-8j3uDsp22ULVfVFN_3fczSr'
    # server location
    server_url = 'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/b5ab2432-7e17-407e-a70a-2f10076a5ae4'

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(server_url)

    """
    Recieve input from user and map search terms to LDA topic distribution.
    This script first recieves input from the user and then maps these string to the exisiting model. 
    The map of this user input is then matched with the maps of connected papers. The papers are ranked in order of relavence to 
    the search term by taking the dot product of the user input map with the map of the respective papers.
    The papers with the highest dot product are recommended and displayed, along with their parts (courtesy of IBM).
    """
    # change path to model and import
    os.chdir('./Models/Modelv2')
    lda = LdaModel.load('modelv2.gensim')

    # change working directory back to main script
    scriptpath = os.path.abspath(__file__)
    dname = os.path.dirname(scriptpath)
    os.chdir(dname)

    # get user input
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
    stub = {}
    print("Creating dataset from text data...")
    # code to convert ini_dict to flattened dictionary
    print(text_data.keys())
    for i, paper in enumerate(text_data['pmc-articleset']['article']):
        try:
            pmid = paper['front']['article-meta']['article-id'][0]["#text"]
            article_title = paper['front']['article-meta']['title-group']['article-title']
            contributor_text = ''
            for contributor in paper['front']['article-meta']['contrib-group']['contrib']:
                surname = contributor['name']['surname']
                firstname = contributor['name']['given-names']
                name_text = surname + ', ' + firstname + '; ' 
                contributor_text = contributor_text + name_text
            stub_text = article_title + ' * ' + contributor_text
            stub[pmid] = stub_text
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

    # analysis of vector space and ranking of papers
    user_vec = np.array([val[1] for val in user_map])
    papers_score = {}
    for key, values in paper_mapping.items():
        paper_vec = np.array([value[1] for value in values])
        dot_product = np.dot(user_vec, paper_vec)
        papers_score[key] = dot_product
    # sort based upon dot_product
    papers_ranking =  {key: val for key, val in sorted(papers_score.items(), key=lambda item: item[1], reverse=True)}

    # extract parts names, methodology, and concepts
    # cleave excessive documents
    filtered_corpus = parts_prep(list(original_corpus.values()))
    for i, text in enumerate(filtered_corpus):
        if len(text) >= 50000:
            filtered_corpus[i] = text[:49998]

    # set id for deployed model
    entity_responses = []
    concept_responses = []
    model_id = '116b1006-b509-463c-b13e-a57f7a6749f3' 
    for textfile in filtered_corpus[:1]:
        response_entity = natural_language_understanding.analyze(
            text=textfile,
            features=Features(entities=EntitiesOptions(limit=1, model=model_id))
            ).get_result()
        response_concept = natural_language_understanding.analyze(
            text=textfile,
            features=Features(concepts=ConceptsOptions(limit=1))
            ).get_result() 
        entity_responses.append(response_entity)
        concept_responses.append(response_concept)
        # print(json.dumps(response_entity, indent=2))
        # print(json.dumps(response_concept, indent=2))


        return stub, entity_responses, concept_responses













