import csv
import os
import json
from collections import defaultdict
import numpy as np
from PorterStemmer import PorterStemmer
import nltk
from bs4 import BeautifulSoup
import re

from nltk.corpus import stopwords
import sys

'''
Code to access cord-19_2020-07-16 data is inspired 
by https://github.com/allenai/cord19/blob/master/README.md

'''

stemmer=PorterStemmer()

def process_text(text):
    stop_word=set(stopwords.words('english'))

    punctuation = '''!`()|-[]×，–°−′£{}·‑®—•“‐″≥;∼≤”‘’:–'"–\‐,<>./+…=-?@#$%^&*_~'''
    for p in punctuation:
        text=text.replace(p, " ")
    # text = re.sub(r'[^\w\s]', '', text)
    text=text.split()
    text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text if word.lower() not in stop_word]
    return text               

def top100(top100_file):
    top100={}
    top100_collection=set()
    
    with open(top100_file,'r') as f_in:
        lines=f_in.readlines()
        for line in lines:
            
            query=line.strip().split()
            if len(query)==0:
                break
            topic=query[0]
            doc_id=query[2]
            if topic not in top100:
                top100[topic]=[doc_id]
            else:
                top100[topic].append(doc_id)
            top100_collection.add(doc_id)
    return top100,top100_collection

def load(collection_folder, top100):
    # cord_uid_to_text = defaultdict(list)
    inverted_index={}
    collection=0
    
    with open(os.path.join(collection_folder,'metadata.csv'),'r',encoding="utf8") as f_in:
        reader = csv.DictReader(f_in)
        # collection=len(list(reader))
        collection=0
        
        for row in reader:
            
            cord_uid = row['cord_uid']
            title = row['title']
            abstract = row['abstract']

            # authors = row['authors'].split('; ')

            if cord_uid in top100:

            # access the full text (if available) for Intro
            
                introduction = []
                if row['pdf_json_files']:
                    for json_path in row['pdf_json_files'].split('; '):
                        try:
                            with open(os.path.join(collection_folder,json_path),'r') as f_json:
                                full_text_dict = json.load(f_json)
                    
                        # grab introduction section from *some* version of the full text
                                for paragraph_dict in full_text_dict['body_text']:
                                    paragraph_text = paragraph_dict['text']
                                    section_name = paragraph_dict['section']
                                    if 'intro' in section_name.lower():
                                        introduction.append(paragraph_text)

                        # stop searching other copies of full text if already got introduction
                            if introduction:
                               break
                        except FileNotFoundError:
                            pass    

                full_text=" "
                for text in introduction:
                    full_text=full_text+text
                
                full_text= full_text+ " " + title+ " " + abstract
                
                full_text=process_text(full_text)
            
            
                
                for word in full_text:
                    if word not in inverted_index:
                        inverted_index[word]={cord_uid:1}
                        #inverted_index[word]={'doc_frequency':len(inverted_index[word])}
                    
                    else:
                        inverted_index[word][cord_uid]=inverted_index[word].get(cord_uid,0)+1
                        #inverted_index[word]['doc_frequency']=len(inverted_index[word])
                
                        
                    
            
                if cord_uid not in inverted_index:
                    inverted_index[cord_uid]={'words_in_doc': len(full_text)}
                else:
                    inverted_index[cord_uid]['words_in_doc']=len(full_text)
                 
                if 'dl_avg' not in inverted_index:
                    inverted_index['dl_avg']=inverted_index[cord_uid]['words_in_doc']
                else:
                    inverted_index['dl_avg']=inverted_index['dl_avg']+inverted_index[cord_uid]['words_in_doc']

            

            collection+=1
            
        inverted_index['dl_avg']=inverted_index['dl_avg']/len(top100)

        return inverted_index, collection

def query_vector(query):
    vector={}
    for term in process_text(query):
        if term not in vector:
            vector[term]=1
        else:
            vector[term]+=1
    return vector
        
def bm25(term, doc, b, k1, N, inverted_index):
    
    w=np.log(N)-np.log(len(inverted_index[term])*N/N_top100)
    tf_i=inverted_index[term][doc]/(inverted_index[doc]['words_in_doc']+0.0001)
    return (tf_i*(1+k1)*w/(k1*((1-b)+b*inverted_index[doc]['words_in_doc']/(inverted_index['dl_avg']+0.0001))+tf_i))




def rank(docs, inverted_index, query_vec):
    # text=process_text(query)   
    scored_docs={}
    
    for doc in docs:
        score=0
        for word in query_vec:
            if word not in inverted_index:
                continue
            if doc in inverted_index[word]:
                score=score+query_vec[word]*bm25(word,doc,b,k1,N, corpus)

        scored_docs[doc]=score
    ranked_docs = {k: v for k, v in sorted(scored_docs.items(), key=lambda item: item[1], reverse=True)}
    return ranked_docs

    


def load_topics(covid19_topics):
    topics=dict()
    with open(covid19_topics,'r') as f:
        content='<r>' + f.read() + '</r>'
    soup= BeautifulSoup(content,'lxml')
    topic=soup.find_all('topic')
    for query in topic:
        topic_no=query.get("number")
        text=query.find_next('query')
        text=text.get_text().strip()
        topics[topic_no]=text
    return topics



def rocchio(relevant, nonrelevant, term, query_vector):
    wt=0 # weight
    r=0
    nr=0
    for doc in relevant:
        if doc in corpus[term]:
            r=r+corpus[term][doc]/(corpus[doc]['words_in_doc']+0.0001)*(np.log(N/(len(corpus[term])*N/N_top100)))
    r=beta*r/R
    for doc in nonrelevant:
        if doc in corpus[term]:
            nr=nr+corpus[term][doc]/(corpus[doc]['words_in_doc']+0.0001)*(np.log(N/(len(corpus[term])*N/N_top100)))
    nr=gamma*nr/NR
    if term in query_vector:
        wt= alpha*query_vector[term]+r-nr
    else:
        wt=r-nr
    #if wt<0:
    #    wt=0
    return wt
        
def updated_query(relevant, nonrelevant,query_vector):
    updated={}
    for term in query_vector:
        updated[term]=rocchio(relevant, nonrelevant,term,query_vector)
    return updated
        

def output(output_file):
    query_file=topics
    top100_for_query=top100_file[0]
    with open(output_file, 'w') as f:
        for queryno in query_file:
            top100_docs=top100_for_query[queryno]
            query=query_file[queryno]
            query_vec=query_vector(query)
            relevant=top100_docs[:R]
            nonrelevant=top100_docs[-1:]
            new_queryvec=updated_query(relevant,nonrelevant,query_vec)
            ranked_docs=rank(top100_docs,corpus,new_queryvec)
            string=" "
            i=1
            for doc in ranked_docs:
                string= queryno + " " + "Q0" + " " + doc + " " + str(i) + " " + str(ranked_docs[doc]) + " " + "runid1"
                f.write(string + "\n")
                i=i+1
    





if __name__== "__main__":
    
    #print(load(sys.argv[1],top100(sys.argv[2])[1]))
    topics= (load_topics(sys.argv[1]))
    top100_file=top100(sys.argv[2])
    
    
    corpus, N= load(sys.argv[3],top100_file[1])
    N_top100=len(top100_file[1])
    k1=2
    b=0.75
    alpha=1
    beta=0.75
    gamma=0.15
    R=99 # relevant docs
    NR=1 # non-relevant docs
    output(sys.argv[4])
    
    
    


