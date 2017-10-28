import pandas as pd
import requests

api_base = 'http://api.gbif.org/v1/'
complement1 = 'occurrence/search?year=2017&limit=300'
request1 = requests.get(api_base + complement1)

results1 = request1.json()['results']
df1 = pd.DataFrame(results1)


complement2 = 'occurrence/search?year=2017&limit=300&offset=300'
request2 = requests.get(api_base + complement2)

results2 = request2.json()['results']
df2 = pd.DataFrame(results2)

df = pd.concat([df1, df2])  # DataFrame com 600 entradas

