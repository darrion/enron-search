import pickle 
import os 
import codecs
import sys
import time
import re
from typing import Protocol 

root_path = "./maildir"

metadata_keys = [
    "Message-ID", 
    "Date", 
    "From", 
    "To", 
    "Subject", 
    "Mime-Version", 
    "Content-Type", 
    "Content-Transfer-Encoding",
    "X-From", 
    "X-To", 
    "X-cc", 
    "X-bcc", 
    "X-Folder", 
    "X-Origin", 
    "X-FileName"
]

EXCLUDED_FILES = [".DS_Store", ".pickle"]

NUM_OF_METADATA_LINES = len(metadata_keys)

TOTAL_FILES = 5174077

def clean(): 

    count = 0 

    for sub_path, super_paths, files in os.walk(root_path):

        for file_obj in files:

            file_path = os.path.join(sub_path, file_obj) 

            if "pickle" in file_path: 
            
                try:
                    os.remove(file_path)
                    print (f"Deleted: {file_path}")
                except: 
                    print (f"Failed to delete: {file_path}")
                    continue 

    print ("Done cleaning.")

def search(term):
    top_word_map = {}
    with open("./maildir/top_terms.pickle", "rb") as top_terms_pickle: 
        top_word_map = pickle.load(top_terms_pickle)
        top_terms_pickle.close()
    return top_word_map[term]

def filter_words(words, exclusions):

    for excluded_word in exclusions:

        words.remove(exclusions)

def is_meta_info(text):

    return ":" in text 

def is_excluded(file_path):

    for exclusion in EXCLUDED_FILES:
        if exclusion in file_path:
            return exclusion in file_path 
    return False 

def format_file_path(file_path):

    return "." + file_path.strip(".").split("/",1)[1]

def is_map_pickle(file_path):

    return file_path.endswith(".map.pickle")

def is_email_map_pickle(file_path):

    return file_path.endswith(".email.map.pickle")

def map_emails():

    file_count = 0 

    for root, children, files in os.walk(root_path):

        for _file_ in files:

            file_path = os.path.join(root, _file_)

            if is_excluded(file_path):
                continue
            
            email_map = {}

            with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file_stream:

                lines = file_stream.readlines()

                for i in range(NUM_OF_METADATA_LINES):
                    
                    line = lines[i]
                    line = line.replace("\r", "").replace("\n", "")
                    split_line = line.split(":",1)      
                    key, value = (split_line[0], None)
                    if len(split_line) > 1:
                        value = split_line[1].strip()
                    email_map[key] = value 
                content = "".join(lines[NUM_OF_METADATA_LINES+1:])
                content_length = len(content) 
                email_map["FilePath"] = file_path 
                email_map["Content"] = content 
                email_map["ContentLength"] = content_length
                file_count+=1
                file_stream.close()

            
            base_file_path = "." + file_path.strip(".")
            email_map_file_path = f"{base_file_path}.email.map.pickle"
            with open(email_map_file_path, 'wb') as file_stream:
                pickle.dump(email_map, file_stream, protocol=pickle.HIGHEST_PROTOCOL)
                file_stream.close()
                
            print(f" {email_map_file_path} {file_count} / {TOTAL_FILES}", flush=True)

def dist_words(): 

    file_count = 0
    word_set = {}

    for root, children, files in os.walk(root_path):

        for _file_ in files:

            email_map_file_path = os.path.join(root, _file_)

            if is_email_map_pickle(email_map_file_path):

                email_map = {}
                word_dist_map = {}

                with open(email_map_file_path, "rb") as file_stream:
                    email_map = pickle.load(file_stream)
                    content = email_map["Content"]
                    content = re.sub("[^\w\s]", "", content)
                    content = content.split()
                    content_length = email_map["ContentLength"] 
                    for word in content:
                        if not word in word_dist_map:
                            word_dist_map[word] = content.count(word) / content_length
                        word_set.add(word)
                    file_stream.close()

                base_file_path = email_map_file_path.strip(".email.map.pickle")
                word_dist_map_file_path = "." + f"{base_file_path}.dist.map.pickle"
                
                with open(word_dist_map_file_path, "wb") as file_stream: 
                    pickle.dump(word_dist_map, file_stream, protocol=pickle.HIGHEST_PROTOCOL)
                    file_stream.close()

                word_set_file_path = "./maildir/words.set.pickle"

                with open(word_set_file_path, "wb") as file_stream:
                    pickle.dump(word_set, file_stream, protocol=pickle.HIGHEST_PROTOCOL)
                    file_stream.close()
                
                file_count+=1
                print(f" {word_dist_map_file_path} {file_count} / {TOTAL_FILES}", flush=True)

def top_words():



#clean()
map_emails()            
dist_words()
