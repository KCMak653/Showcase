import pandas as pd

def nested_get(dic, keys):    
    for key in keys:
        dic = dic[key]
    return dic

def track_df_from_tracks(tracks, df_schema):
    track_dicts =[]
    for track in tracks:
        track_dict = {}
        for col, keys in df_schema.items():
            track_dict[col] = nested_get(track, keys)
        track_dicts.append(track_dict)
    track_df = pd.DataFrame.from_dict(track_dicts)
    return track_df

def get_unique_albums(df, min_tracks = 2):
    # Remove 'albums' with single track
    track_df = df.copy()
    unique_albums = track_df['album_id'].value_counts().to_frame()

    unique_albums=unique_albums.rename(columns={'album_id':'count'})
    unique_albums = unique_albums[unique_albums['count']>=min_tracks]
    unique_albums = pd.merge(unique_albums, track_df, how='left', left_index=True, right_on='album_id'
                    ).drop_duplicates(subset=['album_id'])
    return unique_albums[['album_id', 'album_name']]

def get_album_tracks(tracks):
    
    track_ids = []
    for track in tracks['items']:
        track_ids.append(track['id'])
    return track_ids

def get_track_ids_from_track_list(tracks):
    track_ids = []
    for track in tracks['tracks']:
        track_ids.append(track['id'])
    return track_ids