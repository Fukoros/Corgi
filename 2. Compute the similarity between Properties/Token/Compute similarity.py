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
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?label ?comment ?ontology
WHERE {
    ?prop rdf:type rdf:Property.
    ?prop <http://graph/origin>  ?ontology.
    ?prop rdfs:label ?label.
    OPTIONAL{?prop rdfs:description ?comment}.
}"""

for r in g.query(q):

    data_props[str(r["prop"])] = {"label":r["label"], "comment":"", "domain":set(), "range":set(), "onto": str(r["ontology"])}
    if "comment" in r:
        data_props[str(r["prop"])]["comment"] = r["comment"]



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
    data_props[str(r["prop"])]["domain"].add(str(r["domain"]))


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
    data_props[str(r["prop"])]["range"].add(str(r["range"]))


# # Retrieve the data of the Classes


classes = {}

q = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?label ?comment
WHERE {
    ?prop rdf:type rdf:Class.
    ?prop rdfs:label ?label.
    OPTIONAL{?prop rdfs:description ?comment}.
}"""

for r in g.query(q):

    classes[str(r["prop"])] = {"label":r["label"], "comment":""}
    if "comment" in r:
        classes[str(r["prop"])]["comment"] = r["comment"]



# # Compute the similarity between the Classes

# In[6]:


df_classes = pd.DataFrame.from_dict(classes, orient="index")

df_classes["label doc"] = df_classes["label"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_classes["comment doc"] = df_classes["comment"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_classes["comment not empty"] = df_classes["comment doc"].map(lambda x: len(x) != 0)


# In[7]:


df_classes = df_classes[:10]


# In[8]:


def compute_similarity_classes(name, queue, dict_shared_sim_classes, df_classes, total_length, counter, next_print):

    print(f"Process n°{name} : Launched", flush=True)

    dict_local_sim_classes = {}

    while not queue.empty():

        index, prop_1 = queue.get()

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
            next_print.value+=0.5

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

    for name in range(processes_to_create):
#         x = Process(target=test_p, args=(name,counter))
#         processes.append(x)
#         x.start()
        x = Process(target=compute_similarity_classes, args=(name, q, dict_shared_sim_classes, df_classes, size_queue, counter, next_print))
        processes.append(x)
        x.start()

    for index, process in enumerate(processes):
        process.join()

    print(counter)

    dict_sim_classes = dict(dict_shared_sim_classes)


# In[ ]:


pd.DataFrame.from_dict(dict_sim_classes, orient="index").to_csv("sim_classes.csv")


# In[ ]:


# %%time

# def compute_similarity_classes( index, dict_shared_sim_classes, df_classes):

#     prop_1 = df_classes.index[index]

#     for prop_2 in df_classes[index:]:

#         sim = 0
#         nb_sim = 0

#         sim += df_classes["label doc"].loc[prop_1].similarity(df_classes["label doc"].loc[prop_2])
#         nb_sim += 1

#         if df_classes["comment not empty"].loc[prop_1] and df_classes["comment not empty"].loc[prop_2]:
#             sim += df_classes["comment doc"].loc[prop_1].similarity(df_classes["comment doc"].loc[prop_2])
#             nb_sim += 1

#         sim /= nb_sim

#         dict_shared_sim_classes[(prop_1, prop_2)] = sim
#         dict_shared_sim_classes[(prop_2, prop_1)] = sim

# dict_sim_classes = {}

# # q = Queue()

# # for i, prop_1 in enumerate(df_classes.index):
# #     q.put((i,prop_1))

# # size_queue = q.qsize()


# with Manager() as manager:

#     dict_shared_sim_classes = manager.dict()

#     PROCESSES = 2
#     with multiprocessing.Pool(PROCESSES) as pool:
#         params = [(index,dict_shared_sim_classes, df_classes) for index in range(len(df_classes))]
#         print(len(params))
#         results = [pool.apply_async(compute_similarity_classes, p) for p in params]




# # Compute the sim between properties

# In[44]:


df_props = pd.DataFrame.from_dict(data_props, orient="index")

df_props["onto"].value_counts()


# In[45]:


# %%time

dict_sim_props = {}

df_props = pd.DataFrame.from_dict(data_props, orient="index")

df_props["label doc"] = df_props["label"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_props["comment doc"] = df_props["comment"].map(lambda x: Doc(nlp.vocab, words=preprocess(x)))
df_props["comment not empty"] = df_props["comment doc"].map(lambda x: len(x) != 0)
df_props["domain not empty"] = df_props["domain"].map(lambda x: len(x) != 0)
df_props["range not empty"] = df_props["range"].map(lambda x: len(x) != 0)


# For wikidata we have to use x6 properties because we have direct/statement/.... <br>
# Thus we can reduce the number of prop for the wikidata onto and thus be faster (hopefully)

# In[9]:


df_props = df_props[df_props[["onto"]].apply(lambda x: x["onto"] != "http://wikidata.org" or x.name[:30]=="http://www.wikidata.org/prop/P", axis=1)]



# In[10]:


ontos = list(df_props["onto"].value_counts().index)


# In[ ]:


def compute_similarity_property(name, queue, dict_shared_sim_properties, df_props_1, df_props_2):
    print(f"Process n°{name} : Launched", flush=True)

    dict_local_sim_properties = {}

    while not queue.empty():

        index, prop_1 = queue.get()

        for prop_2 in df_props_2.index:
            sim = 0
            nb_sim = 0

            sim += df_props_1["label doc"].loc[prop_1].similarity(df_props_2["label doc"].loc[prop_2])
            nb_sim += 1

            if df_props_1["comment not empty"].loc[prop_1] and df_props_2["comment not empty"].loc[prop_2]:
                sim += df_props_1["comment doc"].loc[prop_1].similarity(df_props_2["comment doc"].loc[prop_2])
                nb_sim += 1

            if df_props_1["domain not empty"].loc[prop_1] and df_props_2["domain not empty"].loc[prop_2]:
                domain_1, domain_2 = df_props_1["domain"].loc[prop_1], df_props_2["domain"].loc[prop_2]
                sim_domain = -1
                for d_1 in domain_1:
                    for d_2 in domain_2:
                        if (d_1, d_2) in dict_sim_classes:
                            sim_domain = max(sim_domain, dict_sim_classes[(d_1, d_2)])
                if sim_domain != -1:
                    sim += sim_domain
                    nb_sim += 1


            if df_props_1["range not empty"].loc[prop_1] and df_props_2["range not empty"].loc[prop_2]:
                range_1, range_2 = df_props_1["range"].loc[prop_1], df_props_2["range"].loc[prop_2]
                sim_range = -1
                for r_1 in range_1:
                    for r_2 in range_2:
                        if (r_1, r_2) in dict_sim_classes:
                            sim_range = max(sim_range, dict_sim_classes[(r_1, r_2)])
                if sim_domain != -1:
                    sim += sim_range
                    nb_sim += 1

            sim/=nb_sim

            dict_local_sim_properties[(prop_1, prop_2)] = sim

    dict_shared_sim_properties.update(dict_local_sim_properties)

    print(f"Process n°{name} : Finished", flush=True)


# In[10]:


# %%time

ontos = list(df_props["onto"].value_counts().index)

q = Queue()

with Manager() as manager:

    processes_to_create = multiprocessing.cpu_count()-1
    dict_shared_sim_properties = manager.dict()

    for i, onto_1 in enumerate(ontos[:2]):
        df_props_1 = df_props[df_props["onto"]==onto_1]

        for onto_2 in ontos[i+1:2]:
            df_props_2 = df_props[df_props["onto"]==onto_2]

            print(f"Working on {onto_1} & {onto_2} with {len(df_props_1)}x{len(df_props_2)}")
            start = time.time()

            for i, prop_1 in enumerate(df_props_1.index):
                q.put((i,prop_1))

            processes = list()

            for name in range(processes_to_create):
                x = Process(target=compute_similarity_property, args=(name, q, dict_shared_sim_properties, df_props_1, df_props_2))
                processes.append(x)
                x.start()

            for index, process in enumerate(processes):
                process.join()

            end = time.time()
            print(end - start)
        print(f"Finished with {onto_1}")
    print("Finished computation -> Copy the dictionary")
    dict_sim_properties = dict(dict_shared_sim_properties)


# In[15]:


f = open("similarity.ttl", "w", encoding="utf-8")
print("Finished Copy -> Writing result")    
for key in dict_sim_props:
    f.write(f"<{key[0]}> <http://graph/simComputed> <{key[1]}>.\n")
    f.write(f"<< <{key[0]}> <http://graph/simComputed> <{key[1]}> >> <http://graph/sim> {dict_sim_props[key]} .\n")

f.close()


# In[ ]:
