import re
import os
import json
import sys
from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from struct import pack, unpack
import math
import snappy

stemmer=PorterStemmer()

# to check if stemmer is working 
""" word="anannyas"
print(stemmer.stem(word, 0, len(word)-1))

"""


def load(collpath, compression, stopword, xml_tag_info):

    Number_of_docs=0
    

    dictionary={}
    main={}

    posting_list=[]
    

    document_number=None
    
    
    content=None
    

    stop_word=set()
    xml_tag=[]

    text=[]
    posting_pointer=0
    docnames=[]
    
    with open(stopword,'r') as f:
        lines=f.readlines()
        for line in lines:
            stop_word.add(line.strip().lower())

    with open(xml_tag_info,'r') as f:
        lines=f.readlines()
        for line in lines:
            xml_tag.append(line.strip())
    
    for file in os.listdir(collpath):
        with open(os.path.join(collpath,file), 'r') as f:
            content='<r>'+ f.read() + '</r>' 
        soup= BeautifulSoup(content,'xml')
        doc= soup.find_all('DOC')

      #  docno= soup.find_all('DOCNO')
       # for i in range(len(doc)):
       #     print(docno[i].get_text())

       

        for docs in doc:
            docno= docs.find('DOCNO')
            docno=docno.get_text().strip()
            #doc_parts=docno.split("-")
            #docname=doc_parts[0]
            #docid=int(doc_parts[1])
            # dictionary[docno]={}
            #document_number=docname

            docnames.append(docno)
            n=len(docnames)
            
            for i in range(1,len(xml_tag)):
                for tag in docs.find_all(xml_tag[i]):
                    text=tag.get_text()
                    punctuation = '''!`()|-[]{};:'"\,<>./?@#$%^&*_~'''

                #  digits='''0123456789'''
                   # text.replace("'s","").replace("'","").replace("’","").replace('"',"").replace("`","").replace(".","").replace("?","").replace(",","").replace("!","").replace(":","").replace(";","").replace("+","").replace("%","").replace("-"," ").replace("_"," ").replace("~"," ").replace("|"," ").replace("$", "").replace("``", "").replace("'''", "").replace("''", "")
                    
                    for p in punctuation:
                        text=text.replace(p, " ")

                    '''
                    for digit in digits:
                        text=text.replace(digit,"")
                    '''

                    text=text.split()
                    text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text if word.lower() not in stop_word]
                    

                    for word in text:
                        if word not in main:
                            # dictionary[word]=[(document_number, docid, posting_pointer)]
                            if len(posting_list)==0 :
                                posting_list.append(n-1)
                            elif (n-1) != posting_list[-1]:
                                posting_list.append(n-1)

                            main[word]=[len(posting_list)-1]
                            
                            
                            
                        
                            
                        else:
                            if (n-1) != posting_list[main[word][-1]]:
                                if (n-1) != posting_list[-1]:
                                    posting_list.append(n-1)
                                main[word].append(len(posting_list)-1)
                                
                                #posting_pointer+=1
                                
                            
                        
    


    if(compression==0):
        return [main,docnames], posting_list, compression, stop_word
    elif (compression==1):
        return [main,docnames], compression1_encode(posting_list), compression, stop_word
    elif (compression==2):
        return [main,docnames], compression2_encode(posting_list), compression, stop_word
    elif (compression==3):
        return [main,docnames], snappy.compress(compression1_encode(posting_list)), compression, stop_word




def create(indexfile, dictionary, posting_list, compress, stopword):
    with open(indexfile + ".dict", "w") as f:
        f.write((str(compress)+'\n'))
        f.write((str(stopword) + '\n'))
        json.dump(dictionary,f)
    if compress==0:
        with open(indexfile + ".idx", "w") as f:
            json.dump(posting_list,f)
    else:
        with open(indexfile + ".idx", "wb") as f:
            f.write(posting_list)

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



              

if __name__== "__main__":
    if(int(sys.argv[4])>3):
        print("Have not implemented compression 4 and 5")
    else:
        dictionary, posting_list, compression, stopword= load(sys.argv[1], int(sys.argv[4]), sys.argv[3],sys.argv[5] ) 
        create(sys.argv[2], dictionary, posting_list, compression, stopword)     
    
    

        
                








