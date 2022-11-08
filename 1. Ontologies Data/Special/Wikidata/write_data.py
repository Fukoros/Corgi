import re

def write_property(f, dictionary):

    for key in dictionary:
        
        prop_data = dictionary[key]
        id_prop = key.split("/")[-1]
        key = "<http://www.wikidata.org/prop/"+id_prop+">" 
        
        prefixes = ["http://www.wikidata.org/prop/direct/", "http://www.wikidata.org/prop/direct-normalized/", "http://www.wikidata.org/prop/statement/", "http://www.wikidata.org/prop/statement/value/", "http://www.wikidata.org/prop/statement/value-normalized/"]
        for prefixe in prefixes:
            f.write(f'{key} <http://www.graph/alternativeProp> <{prefixe}{id_prop}>.\n')

        
        for label, lang in prop_data["label"]:

            label_to_write = str(label)
            label_to_write = re.sub("\s", " ", label_to_write)
            label_to_write = label_to_write.replace('"',' ')
            label_to_write = label_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> "{label_to_write}"@{lang}.\n')

        f.write(f'<{prop_data["context"]}> <http://www.w3.org/ns/prov#generated> {key}.\n')

        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{prop_data["type"]}>.\n')
        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>.\n')

        for comment, lang in prop_data["comment"]:

            comment_to_write = str(comment)
            comment_to_write = re.sub("\s", " ", comment_to_write)
            comment_to_write = comment_to_write.replace('"',' ')
            comment_to_write = comment_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#description> "{comment_to_write}"@{lang}.\n')

        for domain in prop_data["domain"]:

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#domain> <{domain}>.\n')

        for rang in prop_data["range"]:
            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#range> <{rang}>.\n')

def write_class(f, dictionary):

    for key in dictionary:

        prop_data = dictionary[key]
        key = "<"+key+">"

        for label, lang in prop_data["label"]:

            label_to_write = str(label)
            label_to_write = re.sub("\s", " ", label_to_write)
            label_to_write = label_to_write.replace('"',' ')
            label_to_write = label_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> "{label_to_write}"@{lang}.\n')

        f.write(f'<{prop_data["context"]}> <http://www.w3.org/ns/prov#generated> {key}.\n')

        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Class>.\n')

        for comment, lang in prop_data["comment"]:

            comment_to_write = str(comment)
            comment_to_write = re.sub("\s", " ", comment_to_write)
            comment_to_write = comment_to_write.replace('"',' ')
            comment_to_write = comment_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#description> "{comment_to_write}"@{lang}.\n')
