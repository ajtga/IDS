import pandas as pd
import requests

api_base = 'http://api.gbif.org/v1/'
complement = 'occurrence/search?year=1917,2017'
request = requests.get(api_base + complement)

results = request.json()['results']
request.json().keys()

df = pd.DataFrame(results)
