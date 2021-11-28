import re
import os
import json
import sys
from PorterStemmer import PorterStemmer
from struct import pack, unpack
import math
import snappy
# import time

stemmer=PorterStemmer()

sim=float(1)

def vb_encoding(n):
    byte_stream=[]
    while True:
        byte_stream.insert(0,n%128)
        if n<128:
            break
        n=n//128
    byte_stream[-1]=byte_stream[-1]+128
    return pack('%dB' % len(byte_stream), *byte_stream)
   # return byte_stream


def compression1_encode(list_of_ids):
    byte_stream=[]
    for id in list_of_ids:
        byte_stream.append(vb_encoding(id))
    return b"".join(byte_stream) 

def compression1_decode(byte):
    decode=0
    ids=[]
    byte= unpack('%dB' % len(byte), byte)
    for bit in byte:
        if bit<128:
            decode=decode*128+bit
        else:
            decode=decode*128+(bit-128)
            ids.append(decode)
            decode=0
    return ids


def tobinary(number):
    return int(bin(number).replace("0b",""))   

def lsb(number, l):
    flag= bool(number&(1<<(l-1))) 
    if flag:
        return 1
    else:
        return 0

def length(number_in_binary):
    return (math.floor(math.log2(number_in_binary))+1)

def binary_encoding(n):
    byte_stream=[]
    while True:
        byte_stream.insert(0,n%16)
        if n<16:
            break
        n=n//16
    byte_stream[-1]=byte_stream[-1]+16
    return pack('%dB' % len(byte_stream), *byte_stream)
   # return byte_stream


def compression2_encode(list_of_ids):
    byte_stream=[]
    for id in list_of_ids:
        byte_stream.append(binary_encoding(id))
    return b"".join(byte_stream) 




def compression2_decode(byte):
    decode=0
    ids=[]
    byte= unpack('%dB' % len(byte), byte)
    for bit in byte:
        if bit<16:
            decode=decode*16+bit
        else:
            decode=decode*16+(bit-16)
            ids.append(decode)
            decode=0
    return ids


def load(queryfile, resultfile, indexfile, dictfile):
    
    stopword=[]
    queries=[]
    punctuation = '''!`()|-[]{};:'"\,<>./?@#$%^&*_~'''
    
    with open(queryfile,'r') as f:
        lines=f.readlines()
        for line in lines:
            queries.append(line.strip())
    
    
    with open(dictfile,'r') as f:
        line=f.readlines()
        compression=int(line[0])
        stopword=line[1].strip()
        dictionary,docnames=json.loads(line[2])
    
    if compression==0:
        with open(indexfile, 'r') as f:
        
            
        
            posting_list=json.load(f)
            
    else:
        with open(indexfile, 'rb') as f:
        
            
            if (compression==1):
                posting_list=f.read()
                posting_list=compression1_decode(posting_list)
        
            elif (compression==2):
                posting_list=f.read()
                posting_list=compression2_decode(posting_list)
        
            elif (compression==3):
                posting_list=f.read()
                posting_list=snappy.decompress(posting_list)
                posting_list=compression1_decode(posting_list)
    
    

    with open(resultfile, 'w') as f:
        i=0
        for query in queries:
            documents_fetched=[]
            
            for p in punctuation:
                query=query.replace(p, " ")
            text=query.split()
            text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text if word.lower() not in stopword]
            queryno="Q"+str(i)

            

            if len(text)==1:
                
                documents_fetched=fetch_alldocs(dictionary,text[0],posting_list,docnames)
                #documents_fetched=str(documents_fetched)[1:-1].replace("'","")
                if(len(documents_fetched)>0):
                    
                    for k in range(len(documents_fetched)):
                        string=queryno + " " +  documents_fetched[k].replace("'","") + " " + str(sim)
                        f.write(string+"\n")
                
                

            elif len(text)>1:
                term=text[0]
                documents_fetched=fetch_alldocs(dictionary,term,posting_list,docnames)
        
                for j in range(1,len(text)):
                    documents_fetched=intersect(fetch_alldocs(dictionary,text[j],posting_list,docnames),documents_fetched)
                #documents_fetched=str(documents_fetched)[1:-1].replace("'","")
                if(len(documents_fetched)>0):
                
                    for k in range(len(documents_fetched)):
                        string=queryno+" "+ documents_fetched[k].replace("'","") +" "+ str(sim)
                        f.write(string + "\n")
            i+=1
                

    #return dictionary, posting_list, queries, stopword

def intersect(docs1, docs2):
    if docs1 is not None and docs2 is not None:
        return list(set(docs1)&set(docs2))
    else:
        return []



def fetch_pointers(dictionary, word):
    l=[]
    if word in dictionary:
        l=dictionary[word]
    
    return l

def fetch_docids(pointers, docnames, posting_list):
    l=[]
    for pointer in pointers:
        l.append(docnames[posting_list[pointer]])
    
    return l

def fetch_alldocs(dictionary,word,posting_list,docnames):
    
    documents_fetched=[]
    if word in dictionary:
        pointers=fetch_pointers(dictionary,word)
        documents_fetched=fetch_docids(pointers, docnames,posting_list)
    return documents_fetched


    
if __name__=="__main__":
    #start=time.time()
    load(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    #stop=time.time()
    #print(stop-start)

        