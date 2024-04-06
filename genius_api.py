# built-in
import requests
import os
from multiprocessing import Pool
from time import sleep
# user-installed
import pandas as pd
from tqdm import tqdm
from numpy.random import uniform
from dotenv import load_dotenv

load_dotenv()

# constants
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
NAME_DEMO = __name__

def genius(search_term, per_page=15):
    """
    Collect data from the Genius API by searching for `search_term`.
    **Assumes ACCESS_TOKEN is loaded in environment.
    Parameters
    ----------
    search_term : str
        The name of an artist, album, etc.
    per_page : int, optional
        Maximum number of results to return, by default 15
    Returns
    -------
    list
        All the hits which match the search criteria.
    """
    try:
        genius_search_url = f"http://api.genius.com/search?q={search_term}&" + \
                            f"access_token={ACCESS_TOKEN}&per_page={per_page}"
        response = requests.get(genius_search_url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        json_data = response.json()
        return json_data['response']['hits']
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making request for {search_term}: {e}")
        return []

def genius_to_df(search_term, n_results_per_term=10, verbose=True, savepath=None):
    """
    Generate a pandas.DataFrame from a single call to the Genius API.
    Parameters
    ----------
    search_term : str
        Genius search term
    n_results_per_term : int, optional
        Number of results "per_page" for each search term provided, by default 10
    Returns
    -------
    pandas.DataFrame
        The final DataFrame containing the results.
    """
    try:
        json_data = genius(search_term, per_page=n_results_per_term)
        hits = [hit['result'] for hit in json_data]
        df = pd.DataFrame(hits)
        # expand dictionary elements
        df_stats = df['stats'].apply(pd.Series)
        df_stats.rename(columns={c: 'stat_' + c for c in df_stats.columns}, inplace=True)
        df_primary = df['primary_artist'].apply(pd.Series)
        df_primary.rename(columns={c: 'primary_artist_' + c for c in df_primary.columns}, inplace=True)
        df = pd.concat((df, df_stats, df_primary), axis=1)
        if verbose:
            print(f'PID: {os.getpid()} ... search_term:', search_term)
            print(f"Data gathered for {search_term}.")
        # this is a good practice for numerous automated data pulls ...
        if savepath:
            df.to_csv(os.path.join(savepath, f'genius-{search_term}.csv'), index=False)
        return df
    except Exception as e:
        print(f"Error occurred while processing {search_term}: {e}")
        return pd.DataFrame()

# Rest of the script remains unchanged
