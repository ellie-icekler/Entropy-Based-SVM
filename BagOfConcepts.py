#-*- coding: utf-8 -*-

import gensim
from gensim.models import Word2Vec
from sklearn.feature_extraction import DictVectorizer
from collections import OrderedDict, Counter
import numpy

##############################
#### Corpus Preprocessing ####
##############################


def LemmatizeEnglish(content):
    lem = ' '.join([i.decode('utf-8').split('/')[0] for i in gensim.utils.lemmatize(content)])
    return lem

def Tokenize(corpus):
    tokenized = [i.split() for i in corpus]
    counts = dict()
    for sentence in tokenized:
        for word in sentence:
            if counts.get(word):
                counts[word] += 1
            else:
                counts[word] = 1
    tokenized = [[word for word in sentence if counts.get(word)>1] for sentence in tokenized]
    return tokenized

def Dictionary(tokenized):
    dictionary = gensim.corpora.Dictionary(tokenized)
    # dictionary.save(MakeLogFile("gensimdictionary.dict"))
    return dictionary

# Input: corpus --> list of space separated documents of ALL categories
# corpus --> list of strings ['sentence is sentence', 'sentence 2']
def general_dictionary(corpus):
    tokenized = Tokenize(corpus)
    dictionary = Dictionary(tokenized)
    general_dict = sorted([word for word in dictionary.values()])
    return general_dict

#########################
#### Word2Vec Model ####
#########################

def Read_word2vec(model_path, vector_only=True):
    model = Word2Vec.load(model_path)
    if vector_only:
        word_vectors = model.wv
        del model
        return word_vectors
    else:
        return model 

##########################
#### Cluster Handling ####
##########################

# n_clusters: number of clusters
# labels: list of cluster_id for each data point
# words: words relating to each data point
def cluster_dictionary(n_clusters, labels, words):
    cluster_dict = {}
    for clID in range(n_clusters):
        indices = numpy.where(labels == clID)[0].tolist()
        clustered = [words[i] for i in indices]
        cluster_dict[clID]=clustered
    return cluster_dict

# cluster_dict is in the shape of {cluster_id: ['word1','word2','word3'], ...}
# cluster_dict example {0: [...], 1: [...], ..., 7: ['good', 'excellent', 'amazing',...],}
def word_to_cluster_id_dict(cluster_dict):
    word_to_cluster_id_dict = {}
    for key,val in cluster_dict.items():
        for word in val:
            word_to_cluster_id_dict[word] = key
    return word_to_cluster_id_dict

# example input: sentence = 'The hotel was expensive for the services I received, but the staff was friendly'
# example input cluster_dict (151 clusters)
# mid-point word count: Counter({98: 2, 150: 1, 7: 1, 137: 1, 57: 1, 138: 1, 139: 1})
# example output: X
# array([[0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 2., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 1.]])
def sentence_to_Bag_of_Concepts(sentence, cluster_dict, sparse=False):
    word2idx = word_to_cluster_id_dict(cluster_dict)
    lemmatized_sentence = LemmatizeEnglish(sentence)
    clusterized_sentence = [word2idx.get(word) for word in lemmatized_sentence.split()]
    sent_counter = Counter()
    for clusterized_word in clusterized_sentence:
        sent_counter[clusterized_word] += 1
    vectorizer = DictVectorizer(sparse=sparse)
    vectorizer.fit([OrderedDict.fromkeys(cluster_dict.keys(),1)])
    X = vectorizer.transform(sent_counter)
    return X

# example input: 
# corpus = 
#     ['The hotel was expensive for the services I received, but the staff was friendly',
#     'I stayed here and the bed was very comfy']
# example input cluster_dict (151 clusters)
# mid-point word count: [Counter({98: 2, 150: 1, 7: 1, 137: 1, 57: 1, 138: 1, 139: 1}), Counter({81: 2, 48: 1, 98: 1, 46: 1, 127: 1})]
# example output: X
# array([[0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 2., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 1.],
#        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,
#         1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 2., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.,
#         0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
#         0., 0., 0., 0., 0., 0., 0.]])
def corpus_to_Bag_of_Concepts(corpus, cluster_dict, sparse=False):
    word2idx = word_to_cluster_id_dict(cluster_dict)
    lemmatized_corpus = [LemmatizeEnglish(text) for text in corpus]
    clusterized_corpus = [[word2idx.get(word) for word in lemmatized_sentence.split()] for lemmatized_sentence in lemmatized_corpus]
    corpus_counts = []
    for clusterized_sentence in clusterized_corpus:
        sent_counter = Counter()
        for clusterized_word in clusterized_sentence:
            sent_counter[clusterized_word] += 1
        corpus_counts.append(sent_counter)
    vectorizer = DictVectorizer(sparse=sparse)
    vectorizer.fit([OrderedDict.fromkeys(cluster_dict.keys(),1)])
    X = vectorizer.transform(corpus_counts)
    return X

def Feature_Names(cluster_dict):
    vectorizer = DictVectorizer(sparse=sparse)
    vectorizer.fit([OrderedDict.fromkeys(cluster_dict.keys(),1)])
    cluster_id_features = vectorizer.get_feature_names()
    return cluster_id_features

########################
#### Using Clusters ####
########################

# returns the clusters in word vector form instead of text
def Load_word2vec_clusters(word2vec_model,cluster_dict):
    clusters = []
    for cluster_id in range(len(cluster_dict)):
        clustered_word_vectors = word2vec_model[cluster_dict[cluster_id]]
        clusters.append(clustered_word_vectors)
    return clusters

# gets the word that relates to a word vector
def get_word_from_vector(word2vec_model,word_vector):
    word=word2vec_model.most_similar(positive=[word_vector],topn=1)[0][0]
    return word

if __name__ == '__main__':
    pass
