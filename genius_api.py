# built-in
import requests
import os
import sys

from multiprocessing import Pool
from time import sleep
from requests.exceptions import RequestException

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
    
    **Assumes ACCESS_TOKEN is loaded in environment.**

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
        response.raise_for_status()  # Raise an exception for bad response status codes
        
        json_data = response.json()
        return json_data['response']['hits']
    except RequestException as e:
        print(f"Error occurred for search term '{search_term}': {e}")
        return []

def genius_to_df(search_term, n_results_per_term=10, 
                 verbose=True, savepath=None):
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
        df_stats.rename(columns={c:'stat_' + c for c in df_stats.columns},
                        inplace=True)
        
        df_primary = df['primary_artist'].apply(pd.Series)
        df_primary.rename(columns={c:'primary_artist_' + c 
                                for c in df_primary.columns},
                        inplace=True)
        
        df = pd.concat((df, df_stats, df_primary), axis=1)
        
        if verbose:
            print(f'PID: {os.getpid()} ... search_term:', search_term)
            print(f"Data gathered for {search_term}.")

        # this is a good practice for numerous automated data pulls ...
        if savepath:
            df.to_csv(os.path.join(savepath, f'genius-{search_term}.csv'), 
                    index=False)

        return df
    except Exception as e:
        print(f"Error occurred while processing search term '{search_term}': {e}")
        return pd.DataFrame()

def genius_to_dfs(search_terms, **kwargs):
    """
    Generate a pandas.DataFrame from multiple calls to the Genius API.

    Parameters
    ----------
    search_terms : list of strings
        List of artists (say) to search in Genius.
    
    **kwargs : arguments passed to genius_api.genius_to_df

    Returns
    -------
    pandas.DataFrame
        The final DataFrame containing the results. 
    """

    dfs = []

    # loop through search_terms in question
    for search_term in tqdm(search_terms):
        df = genius_to_df(search_term, **kwargs)
        
        # add to list of DataFrames
        dfs.append(df)

    return pd.concat(dfs)

if __name__ == "__main__":
    search_terms = ['The Beatles', 
                    'Missy Elliot', 
                    'Andy Shauf', 
                    'Slowdive', 
                    'Men I Trust']
    
    # (optional) if you need to pass multiple arguments
    # n = 20
    # args = [(t, n) for t in search_terms]
    # then "unpack" `args` within the function (e.g., args[0])

    with Pool(8) as p:
        results = p.map(genius_to_df, search_terms)
        print("\n Total number of results: ", len(results))

    df_genius = pd.concat(results)

    df_genius.to_csv('./data/genius_data_mp.csv', index=False)
