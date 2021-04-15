import pandas as pd
import jsonlines as jl
from sklearn import preprocessing

data_dir = '../build/data/'
spotify_dir = 'archive/'
lyric_dir = 'genius-expertise/genius-expertise/'


def matchLyrics():
    song_dict = {}
    with open(data_dir + lyric_dir + 'song_info.json') as f:
        for item in jl.Reader(f):
            song_dict[item['url_name']] = item

    lyric_arr = []
    with open(data_dir + lyric_dir+'lyrics.jl') as f:
        for item in jl.Reader(f):
            song_info = song_dict.get(item['song'])
            if song_info:
                new_element = (song_info['title'].lower(), song_info['primary_artist'].replace("-", " ").lower(), item['lyrics'])
                lyric_arr.append(new_element)

    spotify_data = pd.read_csv(data_dir + 'SpotifyFeaturesPreprocessed.csv')
    spotify_dict = {}

    for index, row in spotify_data.iterrows():
        spotify_dict[(row['track_name'].lower(), row['artist_name'].lower())] = index

    spotify_data['lyrics'] = "N/A"

    match_count = 0
    for lyric_tuple in lyric_arr:
        spotify_row = spotify_dict.get((lyric_tuple[0], lyric_tuple[1]))
        if spotify_row:
            match_count = match_count + 1
            spotify_data['lyrics'][spotify_row] = lyric_tuple[2]
    print(match_count)
    spotify_data = spotify_data.drop(['artist_name', 'track_id'], axis=1)
    spotify_data.drop(spotify_data.columns[0], axis=1)
    spotify_data.drop(spotify_data.columns[1], axis=1)
    spotify_data.to_csv(data_dir + 'SpotifyFeaturesLyrics.csv')


def preprocess(filename):
    data = pd.read_csv(data_dir + spotify_dir + filename)

    # map categoricals to ints
    data['genre'] = pd.Categorical(data.genre, ordered=True).codes
    data['key'] = pd.Categorical(data.key, ordered=True).codes
    data['mode'] = pd.Categorical(data["mode"], ordered=True).codes
    data['time_signature'] = pd.Categorical(data.time_signature, ordered=True).codes

    # drop unneeded columns
    data = normalize_cols(data, ['popularity', 'duration_ms', 'loudness', 'tempo'])

    data.to_csv(data_dir + 'SpotifyFeaturesPreprocessed.csv')


def normalize_cols(data, cols):
    for col in cols:
        # Create x, where x the 'scores' column's values as floats
        x = data[[col]].values.astype(float)

        # Create a minimum and maximum processor object
        min_max_scaler = preprocessing.MinMaxScaler()

        # Create an object to transform the data to fit minmax processor
        x_scaled = min_max_scaler.fit_transform(x)

        # Run the normalizer on the dataframe
        data[col] = pd.DataFrame(x_scaled)
    return data


def categorical_to_int(data, col):
    data[col] = len(data) - pd.Categorical(data.genre, ordered=True).codes
    return data


def main():
    preprocess('SpotifyFeatures.csv')
    matchLyrics()



if __name__ == "__main__":
    main()