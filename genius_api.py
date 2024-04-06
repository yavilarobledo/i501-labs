import os
import requests
import pandas as pd
from multiprocessing import Pool
from time import sleep
from numpy.random import uniform
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Constants
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

def genius(search_term, per_page=15):
    """
    Collect data from the Genius API by searching for `search_term`.
    **Assumes ACCESS_TOKEN is loaded in environment.**
    """
    genius_search_url = f"http://api.genius.com/search?q={search_term}&" + \
                        f"access_token={ACCESS_TOKEN}&per_page={per_page}"
    response = requests.get(genius_search_url)
    json_data = response.json()
    return json_data['response']['hits']

def genius_to_df(search_term, n_results_per_term=10):
    """
    Generate a pandas.DataFrame from a single call to the Genius API.
    """
    try:
        json_data = genius(search_term, per_page=n_results_per_term)
        hits = [hit['result'] for hit in json_data]
        df = pd.DataFrame(hits)
        return df
    except Exception as e:
        print(f"Error occurred for {search_term}: {e}")
        return None

def genius_to_dfs(search_terms, n_results_per_term=10, verbose=True):
    """
    Generate a pandas.DataFrame from multiple calls to the Genius API.
    """
    dfs = []
    for search_term in tqdm(search_terms):
        df = genius_to_df(search_term, n_results_per_term)
        if df is not None:
            dfs.append(df)
    return pd.concat(dfs)

if __name__ == "__main__":
    # Example search terms
    search_terms = ['The Beatles', 'Missy Elliot', 'Andy Shauf', 'Slowdive', 'Men I Trust']
    
    # Multiprocessing example
    with Pool(8) as p:
        results = p.map(genius_to_df, search_terms)
        
    # Saving data to a single CSV file
    df_genius = pd.concat(results)
    df_genius.to_csv('./genius_data.csv', index=False)
