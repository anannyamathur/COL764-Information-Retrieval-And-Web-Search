import json

def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def load(folder):
    with open(folder, 'r') as f:
        playlist=json.load(f)
    return playlist

def fetch_top_neighbours():
    
    names=load(playlist_names_folder)
    challenge=load(folder_for_challenge)
    corpus=load(tracks_folder)
    neighbourhood={}
    recommended_500_tracks={} 
    for pid in challenge:
        neighbourhood=set()
        recommended_500_tracks[pid]={}
        for word in challenge[pid]:
            neighbourhood.update(set(names[word]))
        neighbourhood=list(neighbourhood)
        for playlist in neighbourhood:
            for track in corpus[str(playlist)]:
                recommended_500_tracks[pid][track]=recommended_500_tracks[pid].get(track,0)+1
        del neighbourhood
        recommended_500_tracks[pid]=[k for (k, _) in sorted(recommended_500_tracks[pid].items(), key=lambda item: item[1], reverse=True)[:recommendation]]
    
    del corpus
    del challenge
    del names

    dump('string_match.json', recommended_500_tracks)




    

        
            



if __name__=="__main__":
    recommendation=500
    folder_for_challenge='challenge_folder/titles.json'
    playlist_names_folder='processed_datasets/names.json'
    tracks_folder='processed_datasets/tfidf.json'
    fetch_top_neighbours()