import json
import csv

def dump(datafolder, data):
    with open(datafolder,'w') as f:
        json.dump(data, f)

def load(folder):
    with open(folder, 'r') as f:
        playlist=json.load(f)
    return playlist

def recommendations():
    string_match=load(string_match_recommendations)
    item_based=load(item_based_recommendations)
    challenge_set=load(challenge)
    universal_set=load(frequent_tracks)
    challenge_tracks=load(challenge_tracks_folder)
    file= open('submission.csv', 'w', newline='')
    file=csv.writer(file)
    file.writerow(['team_info', 'anmath', 'anannyamathur2000@gmail.com'])
    for pid in [str(play['pid']) for play in challenge_set['playlists']]:
        
        if pid in item_based:
            present=challenge_tracks[pid]
            tracks=[track for track in item_based[pid]]
            if len(tracks)==500:
                file.writerow([pid]+tracks)
            else:
                tracks_to_recommend=[]
                recommend=500-len(tracks)
                
                for track in universal_set:
                    if recommend==0:
                        break
                    if track not in present and track not in tracks:
                        tracks_to_recommend.append(track)
                        recommend=recommend-1
                file.writerow([pid]+ tracks+tracks_to_recommend)

        else :
            tracks=string_match[pid]
            if len(tracks)==500:
                file.writerow([pid]+tracks)
            else:
                tracks_to_recommend=[]
                recommend=500-len(tracks)
                
                for track in universal_set:
                    if recommend==0:
                        break
                    if track not in tracks:
                        tracks_to_recommend.append(track)
                        recommend=recommend-1

                file.writerow([pid]+ tracks+tracks_to_recommend)

if __name__ == "__main__":
    string_match_recommendations='string_match.json'
    item_based_recommendations='item_based_sim.json'
    frequent_tracks='universal_popular_tracks.json'
    challenge='spotify_million_playlist_dataset_challenge/challenge_set.json'
    challenge_tracks_folder='challenge_folder/challenge.json'
    recommendations()
