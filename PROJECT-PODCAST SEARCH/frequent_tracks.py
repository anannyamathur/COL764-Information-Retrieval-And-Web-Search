# In case there are no neighbouring playlists-tracks for a challenge set, top 500 frequent tracks are maintained=universal for all 
import json

def load(folder):
    with open(folder, 'r') as f:
        playlist=json.load(f)
    return playlist

def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def upload():
    corpus=load('processed_datasets/play_track.json')
    frequent={track : len(play) for track,play in corpus.items()}
    frequent={k: v for k, v in sorted(frequent.items(), key=lambda item: item[1], reverse=True)[:N]}
    frequent=[k for k in frequent.keys()]
    dump('universal_popular_tracks.json', frequent)

if __name__=="__main__":
    N=500
    upload()