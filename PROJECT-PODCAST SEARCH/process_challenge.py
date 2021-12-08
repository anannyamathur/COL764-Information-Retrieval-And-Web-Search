import os
import json
import sys
from PorterStemmer import PorterStemmer

stemmer=PorterStemmer()

def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def check_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def process_text(text):
    punctuation = '''!`()|-+=[]{};:'"\,<>./?@#$%^&*_~'''
    for p in punctuation:
        text=text.replace(p, " ")
    text=text.split()
    text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text]
    return text

def load_challenge_set(folder):
    folder_for_saving='challenge_folder'
    check_folder(folder_for_saving)
    folder_challenge= folder_for_saving+'/' +'challenge.json'
    folder_challenge_titles= folder_for_saving +'/' +'titles.json'
    folder_challenge_set= folder+ '/' + 'challenge_set.json'
    with open(folder_challenge_set,'r') as f:
        challenge=json.load(f)
    
    playlist_challenge={}
    playlist_titles={}
    for playlist in challenge['playlists']:
        id=playlist['pid']
        if (playlist['num_samples']==0):
            name= playlist['name']
            playlist_titles[id]=process_text(name)
            continue
        
        
        tracks=[]
        for track in playlist['tracks']:
            tracks.append(track['track_uri'])
        
        playlist_challenge[id]=tracks

    dump(folder_challenge, playlist_challenge)    
    
    dump(folder_challenge_titles, playlist_titles) 

if __name__ == "__main__":
    load_challenge_set(sys.argv[1])