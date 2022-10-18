import re

def write_property(f, dictionary):

    for key in dictionary:

        prop_data = dictionary[key]

        for label in prop_data["label"]:

#             label_prepared = re.sub("\s", " ", label)
#             label_prepared = label_prepared.replace('"'," ")
#             label_prepared = label_prepared.replace('\\'," ")

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> {label}.\n')

        f.write(f'{key} <http://graph/origin> <{prop_data["context"]}>.\n')

        for typ in prop_data["type"]:
            f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> {typ}.\n')
        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>.\n')

        for comment in prop_data["comment"]:

#             comment_prepared = re.sub("\s", " ", comment)
#             comment_prepared = comment_prepared.replace('"'," ")
#             comment_prepared = comment_prepared.replace('\\'," ")

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#description> {comment}.\n')

        for domain in prop_data["domain"]:

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#domain> <{domain}>.\n')

        for rang in prop_data["range"]:
            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#range> <{rang}>.\n')

def write_class(f, dictionary):

    for key in dictionary:

        prop_data = dictionary[key]

        for label in prop_data["label"]:

#             label_prepared = re.sub("\s", " ", label)
#             label_prepared = label_prepared.replace('"'," ")
#             label_prepared = label_prepared.replace('\\'," ")

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> {label}.\n')

        f.write(f'{key} <http://graph/origin> <{prop_data["context"]}>.\n')

        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Class>.\n')

        for comment in prop_data["comment"]:

#             comment_prepared = re.sub("\s", " ", comment)
#             comment_prepared = comment_prepared.replace('"'," ")
#             comment_prepared = comment_prepared.replace('\\'," ")

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#description> {comment}.\n')
