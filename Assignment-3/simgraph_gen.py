import sys
from PorterStemmer import PorterStemmer
import os
import math
#import networkx as nx
#import json

stemmer=PorterStemmer()

'''
def remove_introduction(lines): # To remove the introduction in the beginning
    begin=0
    for i in range(len(lines)):
        if(lines[i] == '\n'):
            begin = i+1
            break
    begin_lines = lines[begin:]
    return begin_lines
'''

def intersect(docs1, docs2):
    if docs1 is not None and docs2 is not None:
        return list(set(docs1)&set(docs2))
    else:
        return []

def union(docs1, docs2):
    if docs1 is not None and docs2 is not None:
        return list(set(docs1)|set(docs2))
    else:
        return []

def process_text(text):
    punctuation = '''!`+()|-[]={};:'"\,<>./?@#$%^&*_~'''
    for p in punctuation:
        text=text.replace(p, " ")
    text=text.strip()
    text=text.split()
    
    text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text]
    return text

def load_collection(directory):
    N=0
    document={}
    collection={}
    
    for file in os.listdir(directory):
        for doc in os.listdir(os.path.join(directory,file)):
            with open(os.path.join(directory,file,doc), 'r') as f:
                lines=f.readlines()
            file_name= str(file)+ '/'+ str(doc)
            document[file_name]={}
            
            #text=remove_introduction(lines)
            text=lines
            
            for line in text:
                for word in process_text(line):
                    document[file_name][word]=document[file_name].get(word,0)+1
                    if word not in collection:
                        collection[word]={file_name:1}
                    else:
                        collection[word][file_name]=collection[word].get(file_name,0)+1
            N=N+1
    return document, collection, N



def jaccard(corpus, output_file):

    #G=nx.Graph()

    f=open(output_file,'w')
    dictionary=list(corpus)
    
    for doc1,doc2 in [ (doc1,doc2) for index, doc1 in enumerate(dictionary) for doc2 in dictionary[index + 1: ]]:
        words_doc1=list(word for word in corpus[doc1])
        words_doc2=list(word for word in corpus[doc2])
        common_terms=intersect(words_doc1,words_doc2)
        
        common_terms=len(common_terms)
        all_terms=len(words_doc1)+len(words_doc2)-common_terms
        if all_terms==0:
            continue
        if common_terms==0:
            continue
        sim= common_terms/all_terms
        sim=round(sim,4)

        #G.add_edge(doc1,doc2,weight=sim)

        text= doc1 + " " + doc2 + " " +str(sim)
        
        f.write(text)
        f.write("\n")
    '''
    pr= nx.pagerank(G,alpha=0.85)
    pr= {k: v for k, v in sorted(pr.items(), key=lambda item: item[1], reverse=True)[:20]}
    with open('pr_jaccard.json','w') as f_in:
        json.dump(pr, f_in)
    '''    

    

def cosine_sim(corpus,  output_file):

    #G=nx.Graph()

    f=open(output_file,'w')
    
    dictionary=list(corpus)
    for doc1,doc2 in [ (doc1,doc2) for index, doc1 in enumerate(dictionary) for doc2 in dictionary[index + 1: ]]:
        sum=0
        denom1=0
        denom2=0
        for word in union([word for word in corpus[doc1]],[word for word in corpus[doc2]]):
            if word in corpus[doc1]:
                denom1=denom1+corpus[doc1][word]**2
            if word in corpus[doc2]:
                denom2=denom2+corpus[doc2][word]**2
            if word in corpus[doc1] and word in corpus[doc2]:
                sum=sum+corpus[doc1][word]*corpus[doc2][word]
            
            
        denom1=math.sqrt(denom1)
        denom2=math.sqrt(denom2)
        if denom1==0 or denom2==0 or sum==0:
            continue
        sim=round(sum/(denom1*denom2),4)



        #G.add_edge(doc1,doc2,weight=sim)

        text= doc1 + " " + doc2 + " " +str(sim)
        
        f.write(text)
        f.write("\n")
            
    '''
    pr= nx.pagerank(G,alpha=0.85)
    pr= {k: v for k, v in sorted(pr.items(), key=lambda item: item[1], reverse=True)[:20]}
    with open('pr_cosine.json','w') as f_in:
        json.dump(pr, f_in)
    '''

def compute_tfidf(corpus, collection):
    values={}
    
    for doc in corpus:
        values[doc]={}
        
        for word in collection:
            idf=math.log2(1+ N/(len(collection[word])+0.00001))
            if word not in corpus[doc]:
                continue
            
            freq=corpus[doc][word]
            tf=1+math.log2(freq) 
            values[doc][word]=tf*idf
            
        
    
    return values

if __name__=='__main__':
    collection_directory=sys.argv[2]
    output_file=sys.argv[3]
    similarity=sys.argv[1]
    corpus, collection, N= load_collection(collection_directory)
    
    
    if similarity=='jaccard':
        del collection
        jaccard(corpus,output_file)
    
    else:
        values=compute_tfidf(corpus,collection)
        del collection
        del corpus
        cosine_sim(values,output_file)