#!/usr/bin/env python
# coding: utf-8

# In[1]:


from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, BASIC

import spacy
from spacy.tokens import Doc
import pandas as pd
import numpy as np
import time


import sys
from multiprocessing import Process, Manager, Queue
import multiprocessing

nlp = spacy.load('en_core_web_lg')

import gensim
import nltk

from tqdm import tqdm

stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords.add("</s>")

def empty_vector(x):
    for i in x:
        if sum(i.vector) == 0:
            return True
    return False

def connected_to_natural(x):
    res = ""
    len_x = len(x)
    for i, carac in enumerate(x):
        if (i >= 1) and (i<(len_x-1)) and (ord(carac)>=ord("A")) and (ord(carac)<=ord("Z")) and (ord(x[i+1])>=ord("a")) and (ord(x[i+1])<=ord("z")):
            res+=" "+carac
        else:
            res+=carac
    return res

def preprocess(text):
    text = connected_to_natural(text)
    return [word for word in gensim.utils.simple_preprocess(text,min_len=1,max_len=50) if word not in stopwords]


# # Retrieve the data of all the properties

# In[2]:


# %%time
g = Graph()
g.parse(source="statements.nt")

data_props = {}

q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?prop ?label ?comment ?ontology
WHERE {
    ?prop rdf:type rdf:Property.
    ?prop <http://graph/origin>  ?ontology.
    ?prop rdfs:label ?label.
    OPTIONAL{?prop rdfs:comment ?comment}.
}"""

for r in g.query(q):

    data_props[r["prop"]] = {"label":r["label"], "comment":"", "domain":set(), "range":set(), "onto": r["ontology"]}
    if "comment" in r:
        data_props[r["prop"]]["comment"] = r["comment"]



# In[3]:


# %%time

q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?domain
WHERE {
    ?prop rdf:type rdf:Property.
    ?prop rdfs:label ?label.
    ?prop rdfs:domain ?domain.
}"""


for r in g.query(q):
    data_props[r["prop"]]["domain"].add(r["domain"])


# In[4]:


# %%time

q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?range
WHERE {
    ?prop rdf:type rdf:Property.
    ?prop rdfs:label ?label.
    ?prop rdfs:range  ?range.
}"""


for r in g.query(q):
    data_props[r["prop"]]["range"].add(r["range"])


# # Retrieve the data of the Classes

# In[5]:

classes = {}

q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?label ?comment
WHERE {
    ?prop rdf:type rdf:Class.
    ?prop rdfs:label ?label.
    OPTIONAL{?prop rdfs:comment ?comment}.
}"""

for r in g.query(q):

    classes[r["prop"]] = {"label":r["label"], "comment":""}
    if "comment" in r:
        classes[r["prop"]]["comment"] = r["comment"]



# # Compute the sim between the Classes

# In[6]:


df_classes = pd.DataFrame.from_dict(classes, orient="index")

df_classes["label doc"] = df_classes["label"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_classes["comment doc"] = df_classes["comment"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_classes["comment not empty"] = df_classes["comment doc"].map(lambda x: len(x) != 0)


# In[7]:


len(df_classes)


# In[8]:


# df_classes = df_classes[:2]

# print(df_classes)


# In[9]:


def compute_similarity_classes(name, queue, dict_shared_sim_classes, df_classes, total_length, counter, next_print, time_keeper):

    print(f"Process n°{name} : Launched", flush=True)

    dict_local_sim_classes = {}

    while not queue.empty():

        index, prop_1 = queue.get()
        # print(prop_1)

        for prop_2 in df_classes[index:].index:

            sim = 0
            nb_sim = 0

            sim += df_classes["label doc"].loc[prop_1].similarity(df_classes["label doc"].loc[prop_2])
            nb_sim += 1

            if df_classes["comment not empty"].loc[prop_1] and df_classes["comment not empty"].loc[prop_2]:
                sim += df_classes["comment doc"].loc[prop_1].similarity(df_classes["comment doc"].loc[prop_2])
                nb_sim += 1

            sim /= nb_sim

            dict_local_sim_classes[(prop_1, prop_2)] = sim
            dict_local_sim_classes[(prop_2, prop_1)] = sim

        ## Every 0.5% we will print the advancement
        counter.value += 1
        if (counter.value/total_length > next_print.value):
            print(next_print.value*100, "%", flush=True)
            print((time.time()-time_keeper.value)/60 , "minute since last print", flush=True)
            time_keeper = time.time()
            next_print.value+=0.1

    dict_shared_sim_classes.update(dict_local_sim_classes)

    print(f"Process n°{name} : Finished", flush=True)


# In[ ]:


# %%time
dict_sim_classes = {}

q = Queue()

for i, prop_1 in enumerate(df_classes.index):
    q.put((i,prop_1))

size_queue = q.qsize()

with Manager() as manager:

    processes_to_create = multiprocessing.cpu_count()-1
    processes = list()

    dict_shared_sim_classes = manager.dict()
    counter = manager.Value("counter",0)
    next_print = manager.Value("next_print",0)
    time_keeper = manager.Value("time",time.time())

    for name in range(processes_to_create):
        x = Process(target=compute_similarity_classes, args=(name, q, dict_shared_sim_classes, df_classes, size_queue, counter, next_print, time_keeper))
        processes.append(x)
        x.start()

    for index, process in enumerate(processes):
        process.join()

    print(counter)



    pd.DataFrame.from_dict(dict(dict_shared_sim_classes), orient="index").to_csv("sim_classes.csv")
