from rdflib import Graph
import pandas as pd
from write_data import *


# The goal of this File is to retrieve the data from every files

folders = pd.read_csv("folders_to_read.csv")

f_prop = open("Properties.nt", "w", encoding="utf-8")
f_class = open("Classes.nt", "w", encoding="utf-8")

for folder, file, context in folders.values:
    print(folder)
    g = Graph()
    g.parse(folder+"/"+file)


    # Retrieve the properties
    dict_prop = {}

    q = """
        SELECT distinct ?prop ?type
        WHERE {

          VALUES ?type { <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>
                         <http://www.w3.org/2002/07/owl#DatatypeProperty>
                         <http://www.w3.org/2002/07/owl#ObjectProperty> }

          ?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type.
        }
        """

    for r in g.query(q):
        if r["prop"].n3() in dict_prop:
            dict_prop[r["prop"].n3()]["type"].add(r["type"].n3())
        else:
            dict_prop[r["prop"].n3()] = {"type":{r["type"].n3()}, "context":context, "label":set(), "comment":set(), "domain":set(), "range":set()}


    q = """
        SELECT distinct ?prop ?label
        WHERE {
          ?prop <http://www.w3.org/2000/01/rdf-schema#label> ?label.

          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>}
        }
        """

    for r in g.query(q):
        dict_prop[r["prop"].n3()]["label"].add(r["label"].n3())

    q = """
        SELECT distinct ?prop ?comment
        WHERE {

          ?prop <http://www.w3.org/2000/01/rdf-schema#comment> ?comment.

          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>}

        }
        """
    for r in g.query(q):
        dict_prop[r["prop"].n3()]["comment"].add(r["comment"].n3())

    q = """
        SELECT distinct ?prop ?label ?domain
        WHERE {

          ?prop <http://www.w3.org/2000/01/rdf-schema#domain> ?domain.

          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>}

        }
        """

    for r in g.query(q):

        dict_prop[r["prop"].n3()]["domain"].add(str(r["domain"]))

    q = """
        SELECT distinct ?prop ?range
        WHERE {

          ?prop <http://www.w3.org/2000/01/rdf-schema#range> ?range.

          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty>}
          UNION
          {?prop <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty>}

        }
        """

    for r in g.query(q):

        dict_prop[r["prop"].n3()]["range"].add(str(r["range"]))

    print("\t", len(dict_prop), "properties found.")
    write_property(f_prop, dict_prop)

    # Retrieve Classes

    dict_classes = {}

    q = """
        SELECT distinct ?class ?label
        WHERE {
          ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label.

          {?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>}
          UNION
          {?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2000/01/rdf-schema#Class>}
        }
        """

    for r in g.query(q):

        dict_classes[r["class"].n3()] = {"label":{r["label"].n3()}, "comment":set(), "context":context}

    q = """
        SELECT distinct ?class  ?comment
        WHERE {

          ?class <http://www.w3.org/2000/01/rdf-schema#comment> ?comment.

          {?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>}
          UNION
          {?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2000/01/rdf-schema#Class>}

        }
        """

    for r in g.query(q):

        dict_classes[r["class"].n3()]["comment"].add(r["comment"].n3())


    print("\t", len(dict_classes), "classes found.")
    write_class(f_class, dict_classes)

f_prop.close()
f_class.close()
