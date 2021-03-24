import pandas as pd
from sklearn import preprocessing

data_dir = './build/data/'
spotify_dir = 'archive/'


def combineFeatures():
    # read the billboard audio features file
    billboard_data = pd.read_csv(data_dir + spotify_dir + 'BillboardAudioFeatures.csv')
    # rename the billboard audio features file
    billboard_data = billboard_data.rename(
        columns={"Performer": "artist_name", "Song": "track_name", "spotify_genre": "genre",
                 "spotify_track_id": "track_id", "spotify_track_popularity": "popularity",
                 "spotify_track_duration_ms": "duration_ms"})

    # drop the columns from the billboard data set that are not in the Kaggle Dataset
    billboard_data = billboard_data.drop(
        ['SongID', 'spotify_track_preview_url', 'spotify_track_album', 'spotify_track_explicit',
         'time_signature'], axis=1)

    # reformat the data columns in the billboard data to match the kaggle
    # everything ended ups getting changed with the pre=processing anyways... so need to figure out what to update
    di = {0: "Minor", 1: "Major"}
    billboard_data['mode'] = billboard_data['mode'].map(di)
    
    # delete the rows that have no values for the audio features
    dict = {"" : 'nan'}
    billboard_data = billboard_data.replace(dict)
    billboard_data = billboard_data.dropna()
    billboard_data = billboard_data.reset_index()
    billboard_data = billboard_data.drop(billboard_data.columns[0], axis=1)
    
    # creating a dictionary to rename the genres in the billboard file
    final_attempt = {}
    index = -1
    for row in billboard_data.itertuples():
        index = index + 1
        #print(index)
        #print(row[3])
        if 'a capella' in row[3]:
            final_attempt[index] = 'A Capella'
        elif 'alternative' in row[3]:
            final_attempt[index] = 'Alternative'
        elif 'anime' in row[3]:
            final_attempt[index] = 'Anime'
        elif 'blues' in row[3]:
            final_attempt[index] = 'Blues'
        elif 'childrens music' in row[3]:
            final_attempt[index] = "Children's Music"
        elif 'classical' in row[3]:
            final_attempt[index] = 'Classical'
        elif 'comedy' in row[3]:
            final_attempt[index] = 'Comedy'
        elif 'country' in row[3]:
            final_attempt[index] = 'Country'
        elif 'dance' in row[3]:
            final_attempt[index] = 'Dance'
        elif 'electronic' in row[3]:
            final_attempt[index] = 'Electronic'
        elif 'folk' in row[3]:
            final_attempt[index] = 'Folk'
        elif 'hip hop' in row[3]:
            final_attempt[index] = 'Hip-Hop'
        elif 'indie' in row[3]:
            final_attempt[index] = 'Indie'
        elif 'jazz' in row[3]:
            final_attempt[index] = 'Jazz'
        elif 'movie' in row[3]:
            final_attempt[index] = 'Movie'
        elif 'opera' in row[3]:
            final_attempt[index] = 'Opera'
        elif 'pop' in row[3]:
            final_attempt[index] = 'Pop'
        elif 'r&b' in row[3]:
            final_attempt[index] = 'R&B'
        elif 'rap' in row[3]:
            final_attempt[index] = 'Rap'
        elif 'reggae' in row[3]:
            final_attempt[index] = 'Reggae'
        elif 'reggaeton' in row[3]:
            final_attempt[index] = 'Reggaeton'
        elif 'rock' in row[3]:
            final_attempt[index] = 'Rock'
        elif 'ska' in row[3]:
            final_attempt[index] = 'Ska'
        elif 'soul' in row[3]:
            final_attempt[index] = 'Soul'
        elif 'soundtrack' in row[3]:
            final_attempt[index] = 'Soundtrack'
        elif 'world' in row[3]:
            final_attempt[index] = 'World'
        else:
            final_attempt[index] = 'Other'
    
    #print(final_attempt)
    
    # adding in a new column to be able to map the genre values to 
    billboard_data['new_genre'] = "N/A"
    for i in range(0,23565):
        billboard_data['new_genre'][i] = i
    # mapping the genre values to the correct row
    billboard_data['new_genre'] = billboard_data['new_genre'].map(final_attempt)
    
    # dropping the old genre column and renaming to have the same column header format
    billboard_data = billboard_data.drop(
        ['genre'], axis=1)
    billboard_data = billboard_data.rename(
        columns={"new_genre": "genre"})
    
    # read the kaggle data set to prepare to append the new rows
    kaggle_data = pd.read_csv(data_dir + spotify_dir + 'SpotifyFeatures.csv')
    kaggle_data = kaggle_data.drop(['time_signature'], axis=1)

    # append the billboard data to the kaggle data
    kaggle_data = kaggle_data.append(billboard_data)

    # save the data to a new file and use this for the rest of the code
    # the test.csv is just for me to check the billboard data
    billboard_data.to_csv(data_dir + spotify_dir + 'test.csv')
    kaggle_data.to_csv(data_dir + spotify_dir + 'ExtraSpotifyData.csv')


def preprocess(filename):
    data = pd.read_csv(data_dir + spotify_dir + filename)

    # update the key
    d1 = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    data['key'] = data['key'].replace(d1)

    d2 = {"Minor": 0, "Major": 1}
    data['mode'] = data['mode'].map(d2)

    # map categoricals to ints
    data['genre'] = pd.Categorical(data.genre, ordered=True).codes

    data = normalize_cols(data, ['popularity', 'duration_ms', 'loudness', 'tempo'])

    data.to_csv(data_dir + 'SpotifyFeaturesPreprocessed.csv')


def matchBillboard():
    billboard_data = pd.read_csv(data_dir + 'BillboardHits.csv')

    billboard_arr = []
    for index, row in billboard_data.iterrows():
        new_element = [row['Song'].lower(), row['Performer'].lower()]
        billboard_arr.append(new_element)

    spotify_data = pd.read_csv(data_dir + 'SpotifyFeaturesPreprocessed.csv')
    spotify_dict = {}

    # I think we also need to match on genre because right now it is only updating one instance of a song
    # or when we remove duplicates we need to keep the instance thats has the 1 for accurate results
    for index, row in spotify_data.iterrows():
        spotify_dict[(row['track_name'].lower(), row['artist_name'].lower())] = index

    spotify_data['billboardhit'] = 0

    match_count = 0
    for billboard_tuple in billboard_arr:
        spotify_row = spotify_dict.get((billboard_tuple[0], billboard_tuple[1]))
        if spotify_row:
            match_count = match_count + 1
            spotify_data['billboardhit'][spotify_row] = 1

    print(match_count)
    # spotify_data = spotify_data.drop(['artist_name', 'track_id'], axis=1)
    spotify_data = spotify_data.drop(spotify_data.columns[0], axis=1)
    spotify_data = spotify_data.drop(spotify_data.columns[0], axis=1)

    spotify_data.to_csv(data_dir + 'SpotifyFeaturesBillboard.csv')


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
    combineFeatures()
    preprocess('ExtraSpotifyData.csv')
    matchBillboard()

if __name__ == "__main__":
    main()