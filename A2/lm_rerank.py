import csv
import os
import json
from collections import defaultdict
import numpy as np
from PorterStemmer import PorterStemmer
import nltk
from bs4 import BeautifulSoup


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
                
                        
                    
            
                if 'words_in_doc' not in inverted_index:
                    inverted_index['words_in_doc']={cord_uid: len(full_text)}
                else:
                    inverted_index['words_in_doc'][cord_uid]=len(full_text)
                 
                if 'dl_avg' not in inverted_index:
                    inverted_index['dl_avg']=inverted_index['words_in_doc'][cord_uid]
                else:
                    inverted_index['dl_avg']=inverted_index['dl_avg']+inverted_index['words_in_doc'][cord_uid]

            

            collection+=1
            
        inverted_index['dl_avg']=inverted_index['dl_avg']/len(top100)

        return inverted_index, collection



    


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


def query_expansion(limit):
    S=N_top100 #No of relevant docs
    
    weights={}
    for word in corpus:
        if word=='words_in_doc' or word=='dl_avg':
            continue
        s=len(corpus[word]) # no of relevant docs that contain the word
        df=s*N/S # no of docs that contain the word = approximation
        numerator= (s+0.5)/(S-s+0.5)
        denominator= (df-s+0.5)/(N-df-S+s+0.5)
        c=np.log(numerator/denominator)
        weights[word]=s*c
   # ranked_wt={k: v for k, v in sorted(weights.items(), key=lambda item: item[1], reverse=True)}
    return list(dict(sorted(weights.items(), key=lambda x: x[1], reverse=True)[:limit]).keys())

def expansion(query,limit,docs):
    weights={}
    for word in expanded_query:
        weights[word]= p_w_R_iid(word,query,docs)
    return list(dict(sorted(weights.items(), key=lambda x: x[1], reverse=True)[:limit]).keys())


def P_term_M (term, document): # calculate P(t|M)
    freq_t_C=0
    freq_t_d=0
    for doc in corpus[term]:
        
        freq_t_C=freq_t_C+corpus[term][doc]
    
    if document in corpus[term]:
        freq_t_d= corpus[term][document]
    P_t_C=freq_t_C/N_top100
    dj=corpus['words_in_doc'][document]
    return ((freq_t_d+mu*P_t_C)/(dj+mu))
 
def p_w(word): # calculate P(w)
    
    sum=0
    for doc in corpus[word]:
        
        sum=sum+P_term_M(word,doc)
    

    return sum/N_top100

def p_w_collection(inverted_index):
    p={}
    for word in inverted_index:
        if word=='dl_avg' or word=='words_in_doc':
            continue
        p[word]=p_w(word)
    return p
    

def p_M_w(word, doc): # P(M|w)
    return p[word]*P_term_M(word,doc)*N_top100 #P(M)=1/N_top100

def p_w_R(word, processed_query,docs): # P(w|R) # conditional sampling
    product=1
    for term in processed_query:
        sum=0
        for doc in docs:
            if word not in corpus or term not in corpus:
                continue
            if doc in corpus[word] and doc in corpus[term]:
                sum=sum+p_M_w(word,doc)*P_term_M(term,doc)
        if sum>0:
            product=product*sum
    return p[word]*product

def p_w_R_iid(word, processed_query, docs): # P(w|R) iid sampling
    sum=0
    for doc in docs:
        product=1
        for term in processed_query:
            if word not in corpus or term not in corpus:
                continue
            if doc in corpus[word] and doc in corpus[term]:
                product=product*P_term_M(term,doc)
        sum=sum+1/N_top100*P_term_M(word, doc)*product
    return sum


def rerank(query,docs,rm):
    scored_docs={}
    
    for doc in docs:
        score=0
        for word in expanded_query:
            
            if doc in corpus[word]:
                if (rm=='rm1'):
                    score=score+p_w_R_iid(word,query,docs)*np.log(P_term_M(word,doc))
                else:
                    score=score+p_w_R(word,query,docs)*np.log(P_term_M(word,doc))
        scored_docs[doc]=score

    ranked_docs = {k: v for k, v in sorted(scored_docs.items(), key=lambda item: item[1], reverse=True)}
    return ranked_docs
        
def output(output_file, expansion_file,rm):
    
    query_file=topics
    top100_for_query=top100_file[0]
    
    with open(expansion_file,'w') as f_ex:
        for topic in topics:
            query= process_text(topics[topic])
            string= topic + ":"
            s=" "
            added_query_terms=expansion(query, 10, top100_for_query[topic])
            for term in added_query_terms:
                if term not in query:
                    s= s+ term
                    s=s+ ","
                    query.append(term)
            s=s.strip()
            if len(s)>0:
                s=s[:-1]
            string=string + " " + s
            f_ex.write(string + "\n")
    
    
    with open(output_file, 'w') as f:
        for queryno in query_file:
            top100_docs=top100_for_query[queryno]
            query=query_file[queryno]
            
            
            ranked_docs=rerank(query,top100_docs,rm)
            string=" "
            i=1
            for doc in ranked_docs:
                string= queryno + " " + "Q0" + " " + doc + " " + str(i) + " " + str(ranked_docs[doc]) + " " + "runid1"
                f.write(string + "\n")
                i=i+1          


                    


                    



                

        


    





if __name__== "__main__":
    
    #print(load(sys.argv[1],top100(sys.argv[2])[1]))
    topics= (load_topics(sys.argv[2]))
    top100_file=top100(sys.argv[3])
    
    corpus, N= load(sys.argv[4],top100_file[1])
    N_top100=len(top100_file[1])
    mu= corpus['dl_avg'] # Smoothing parameter
    expanded_query=query_expansion(20)
    rm=sys.argv[1]
    if(rm!='rm1'):
        p=p_w_collection(corpus)
    output(sys.argv[5], sys.argv[6], rm)
    

