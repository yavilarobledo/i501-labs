# Importing libraries
import os
import requests
import pandas as pd
from multiprocessing import Pool
from time import sleep
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

# Function to retrieve data from the Genius API for a single search term
def get_genius_data(search_term):
    try:
        url = f"http://api.genius.com/search?q={search_term}&access_token={ACCESS_TOKEN}"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        hits = data.get('response', {}).get('hits', [])
        return hits
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for '{search_term}': {e}")
        return []

# Function to process a single search term and save the results to a CSV file
def process_search_term(search_term):
    hits = get_genius_data(search_term)
    df = pd.DataFrame(hits)
    if not df.empty:
        df.to_csv(f'{search_term}_genius_data.csv', index=False)
        print(f"Data saved for '{search_term}'")
    else:
        print(f"No data found for '{search_term}'")

# Function to retrieve data for multiple search terms using multiprocessing
def get_genius_data_multiprocessing(search_terms):
    with Pool() as pool:
        pool.map(process_search_term, search_terms)

if __name__ == "__main__":
    # List of search terms
    search_terms = ['The Beatles', 'Missy Elliot', 'Andy Shauf', 'Slowdive', 'Men I Trust']
    
    # Retrieve data for multiple search terms using multiprocessing
    get_genius_data_multiprocessing(search_terms)
