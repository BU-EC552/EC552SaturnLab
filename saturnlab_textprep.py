# this is a python script that holds functions for parsing and managing text in NLP uses
from Bio import Entrez

def bow_corpus(original_corpus):
    docs = list(original_corpus)
    # Tokenize the documents.
    # Split the documents into tokens.
    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]
    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 2] for doc in docs]
    # Remove stopwords 
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english') + ['fig', 'supplementary']
    docs = [[token for token in doc if token not in stop_words] for doc in docs]
    # Lemmatize the documents.
    from nltk.stem.wordnet import WordNetLemmatizer
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

    from gensim.corpora import Dictionary
    # Remove rare and common tokens.
    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=2, no_above=0.5)
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
    user_array = np.array(user_terms)
    user_corpus = [np.roll(user_array, i) for i in range(len(user_terms))]
    user_corpus = [list(arr) for arr in user_corpus]
    # create dictionary and bag-of-words
    dictionary = Dictionary(user_corpus)
    text_corpus = [dictionary.doc2bow(doc) for doc in user_corpus]
    return text_corpus

def search(query):
    Entrez.email = 'clp0216@bu.edu'
    handle = Entrez.esearch(db='pmc',
                            sort='relevance',
                            retmax='300',
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

# prepare corpus for parts filtering and selection
def parts_prep(practice_corpus):
    docs = list(practice_corpus)
    # Tokenize the documents.
    from nltk.tokenize import RegexpTokenizer
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english') + ['fig', 'supplementary']
    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    for idx in range(len(docs)):
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.
    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]
    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 2] for doc in docs]
    # Remove stop words
    docs = [[token for token in doc if token not in stop_words] for doc in docs]
    # Lemmatize the documents.
    from nltk.stem.wordnet import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]
    filtered_corpus = [" ".join(doc) for doc in docs]
    return filtered_corpus