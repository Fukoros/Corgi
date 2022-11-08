import re

def write_property(f, dictionary):

    for key in dictionary:

        prop_data = dictionary[key]

        for label in prop_data["label"]:

            lang = "en"
            if label._language:
                lang = label._language

            label_to_write = str(label)
            label_to_write = re.sub("\s", " ", label_to_write)
            label_to_write = label_to_write.replace('"',' ')
            label_to_write = label_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> "{label_to_write}"@{lang}.\n')

        f.write(f'<{prop_data["context"]}> <http://www.w3.org/ns/prov#generated> {key}.\n')

        for typ in prop_data["type"]:
            f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> {typ}.\n')
        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>.\n')

        for comment in prop_data["comment"]:

            lang = "en"
            if comment._language:
                lang = comment._language

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

        for label in prop_data["label"]:

            lang = "en"
            if label._language:
                lang = label._language

            label_to_write = str(label)
            label_to_write = re.sub("\s", " ", label_to_write)
            label_to_write = label_to_write.replace('"',' ')
            label_to_write = label_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#label> "{label_to_write}"@{lang}.\n')

        f.write(f'<{prop_data["context"]}> <http://www.w3.org/ns/prov#generated> {key}.\n')

        f.write(f'{key} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Class>.\n')

        for comment in prop_data["comment"]:

            lang = "en"
            if comment._language:
                lang = comment._language

            comment_to_write = str(comment)
            comment_to_write = re.sub("\s", " ", comment_to_write)
            comment_to_write = comment_to_write.replace('"',' ')
            comment_to_write = comment_to_write.replace('\\',' ')

            f.write(f'{key} <http://www.w3.org/2000/01/rdf-schema#description> "{comment_to_write}"@{lang}.\n')
