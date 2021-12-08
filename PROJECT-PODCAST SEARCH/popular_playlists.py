
import json


def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def load_challenge_set():
    with open(challenge_folder, 'r') as f:
        challenge=json.load(f)
    return challenge

def load_index_file():
    with open(playlist_track_folder, 'r') as f:
        playlist=json.load(f)
    return playlist

def load_details():
    with open(playlists_details_folder, 'r') as f:
        playlist_detail=json.load(f)
    return playlist_detail

def popular():
    playlists={}
    for pid in challenge_pids:
        # suggested tracks
        tracks= challenge_pids[pid]
        neighbourhood=set()
        for track in tracks:
            neighbourhood.update(set([id for id in corpus[track]]))
        
        recent=[(details[id]['modified_at'], id) for id in neighbourhood ]
        del neighbourhood
        recent=sorted(recent, reverse=True)[:m]
        playlists[pid]=[id for (_,id) in recent ]
        del recent
        
    dump('popular_playlists.json', playlists)    




if __name__ == "__main__":
    # discover popular playlists on the basis of time of modification(most recently edited must be given preference)
    m=4000 # Neighbourhood size
    challenge_folder='challenge_folder/challenge.json'
    playlist_track_folder='processed_datasets/play_track.json'
    playlists_details_folder='processed_datasets/playlists.json'
    corpus=load_index_file()
    challenge_pids=load_challenge_set()
    details=load_details()
    popular()