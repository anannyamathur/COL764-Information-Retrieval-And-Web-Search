import json
import math


def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def load(folder):
    with open(folder, 'r') as f:
        playlist=json.load(f)
    return playlist

def cosine_similarity():

    challenge=load(challenge_folder)
    corpus=load(playlist_track_folder)
    popular=load(popular_playlists)

    sim={}
    for pid in popular:
        sim[pid]={}
        tracks=challenge[pid]
        for playlist in popular[pid]:
            denom=math.sqrt(sum(x**2 for x in corpus[playlist].values()))
            num=sum(corpus[playlist][track] for track in tracks if track in corpus[playlist])
            sim[pid][playlist]=num/denom
    
    
    # compute neighbours which are nearest
    

    
    
    del popular

    recommended_tracks={}

    for pid in sim:
        similarity={}
        similarity[pid]={k: v for k, v in sorted(sim[pid].items(), key=lambda item: item[1], reverse=True)[:neighbours]}
        recommended_tracks[pid]={}
        tracks=set(challenge[pid])
        filtered_tracks=set()
        for neighbour in similarity[pid]:
            filtered_tracks.update(set([track for track in corpus[neighbour]]))
        filtered_tracks=filtered_tracks-tracks
            
            
        for track in filtered_tracks:
            if track not in recommended_tracks[pid]:
                recommended_tracks[pid][track]=0
            
            rank_score=sum(similarity[pid][neighbour_id] for neighbour_id in similarity[pid] if track in corpus[neighbour_id])
            recommended_tracks[pid][track]+=rank_score
        
        del similarity
        recommended_tracks[pid]={k: v for k, v in sorted(recommended_tracks[pid].items(), key=lambda item: item[1], reverse=True)[:recommendation]}

    del sim
    del corpus
    del challenge
    
    dump('item_based_sim.json', recommended_tracks)   
    

if __name__ == "__main__":
    recommendation=500
    neighbours=100
    
    playlist_track_folder='processed_datasets/tfidf.json'
    popular_playlists= 'popular_playlists.json'
    challenge_folder='challenge_folder/challenge.json'
    
   
    cosine_similarity()
