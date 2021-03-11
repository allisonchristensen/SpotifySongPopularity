import numpy as np
import os  # used for navigating to image path
import pandas as pd
from sklearn import preprocessing

image_dir = './archive/'

def preprocess(filename):
    processed_set = []
    data = pd.read_csv(image_dir + filename)

    # map categoricals to ints
    data['genre'] = pd.Categorical(data.genre, ordered=True).codes
    data['key'] = pd.Categorical(data.key, ordered=True).codes
    data['time_signature'] = pd.Categorical(data.time_signature, ordered=True).codes

    # drop unneeded columns
    data = data.drop(['artist_name', 'track_name', 'track_id', 'mode'], axis=1)
    
    data = normalize_cols(data, ['popularity', 'duration_ms', 'loudness', 'tempo'])

    data.to_csv('SpotifyFeaturesPreprocessed.csv')


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
    


if __name__ == "__main__":
    main()