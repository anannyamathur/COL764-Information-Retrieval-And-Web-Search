import os
import json
import sys
import math
from PorterStemmer import PorterStemmer

stemmer=PorterStemmer()

def process_text(text):
    punctuation = '''!`()|-+=[]{};:'"\,<>./?@#$%^&*_~'''
    for p in punctuation:
        text=text.replace(p, " ")
    text=text.split()
    text=[stemmer.stem(word.lower(),0,len(word)-1) for word in text]
    return text

def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def check_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    


def load_dataset(dataset):

    folder_for_datasets= str(dataset)+'/'
    folder_for_saving='processed_datasets'
    
    folder_playlists= folder_for_saving+'/' +'playlists.json'
    folder_track_playlists=folder_for_saving+'/' +'play_track.json'
    folder_tfidf=folder_for_saving + '/'+ 'tfidf.json'
    folder_names=folder_for_saving+'/'+ 'names.json'
    playlists={}
    playlist_track={}
    tf_idf={}
    name={}

    for file in os.listdir(folder_for_datasets):
        if file.startswith("mpd.slice.") and file.endswith(".json"):
            filepath= os.sep.join((folder_for_datasets,file))
            with open(filepath, 'r') as f:
                toread= json.load(f)
            playlist_collection= toread['playlists']
            for play in playlist_collection:
                play_id=play['pid']
                if play_id not in playlists:
                    playlists[play_id]={}
                    tf_idf[play_id]={}

                if play_id in playlists:
                    playlists[play_id]['num_tracks']=play['num_tracks']
                    playlists[play_id]['modified_at']=play['modified_at']
                    
                
                for track in play['tracks']:
                    trackid= track['track_uri']
                    if trackid not in playlist_track:
                        playlist_track[trackid]={play_id: 1}
                    else :
                        playlist_track[trackid][play_id]=playlist_track[trackid].get(play_id,0)+1
                    
                    tf=1/(s+playlists[play_id]['num_tracks'])
                    idf=math.log(N/len(playlist_track[trackid]))
                    tf_idf[play_id][trackid]=tf*idf
                
                for word in process_text(play['name']):
                    if word in name:
                        name[word].append(play_id)
                    else:
                        name[word]=[play_id]

    check_folder(folder_for_saving)
    
    dump(folder_names, name)
    del name

    dump(folder_playlists,playlists)
    del playlists
    dump(folder_track_playlists,playlist_track)
    del playlist_track                 
    dump(folder_tfidf,tf_idf)   
        
if __name__=="__main__":
    s=50
    N=1000000
    load_dataset(sys.argv[1])


