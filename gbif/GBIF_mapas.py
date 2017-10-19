# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 14:43:37 2017

@author: albuq
"""

# %% Importando bibliotecas
# %%
import pandas as pd
import os
import numpy as np
from plotly.graph_objs import *
from plotly.offline import plot


def mapa(df):
    """Esta função usa das colunas latitude, longitudes e genus do dataframe
    para projetar um mapa com as marcações de localização"""
    mpt = 'pk.eyJ1IjoiYWRlbHNvbmpyIiwiYSI6ImNqNTV0czRkejBnMnkzMnBtdXdsbmRlbDcifQ.Ox8xbLTD_cD7h3uEz13avQ'

    data = Data([Scattermapbox(lat=df.decimalLatitude, lon=df.decimalLongitude,
    mode='markers', marker=Marker(size=10, color='rgb(0, 90, 40)'),
    text=df.genus,)])
    layout = Layout(autosize=True,hovermode='closest',
    mapbox=dict(accesstoken=mpt,bearing=0,center=dict(lat=-9.62,lon=-37.7),
    pitch=0,zoom=4, style='outdoors'),)
    fig=dict(data=data,layout=layout)
    plot(fig)


# Definindo o diretório
#
try:
    os.chdir("C:\\Users\\albuq\\OneDrive\\UFAL\\ENGENHARIA_AMBIENTAL_E_SANITÁRIA\\QUINTO_PERIODO\\INTRODUCAO_A_CIENCIA DE DADOS\\CODANDO\\DADOS")
except:
    pass
# Importando os dados
# %% #problema algumas linhas #
mag = pd.read_csv("df_novo.zip", compression='zip', sep=";", error_bad_lines=False, low_memory=False)

# Colunas
# %%
mag.columns
colunas = list(mag.columns.values)

# Registros de ocorrência até o nível de espécie
# %%
mag_sp = mag[mag["taxonRank"] == "SPECIES"]
del mag

# Selecionando colunas
# %%
mag_sp = mag_sp.loc[:, ["gbifID", "basisOfRecord", "eventDate", "year", "month", "date", "stateProvince", "municipality", "locality", "decimalLatitude", "decimalLongitude", "scientificName", "Kingdom", "phylum", "class", "order", "family", "genus", "species"]]

# Ordenado pelos nomes das espécies
# %%
mag_sp.sort_values("species", inplace=True)

# Criando um id para cada espécie
# %%
mag_sp['id'] = mag_sp.groupby("species").ngroup()
mag_sp = mag_sp.drop_duplicates(['decimalLatitude', 'decimalLongitude', 'species'])
mag_sp = mag_sp[mag_sp['decimalLatitude'] != '0']
mapa(mag_sp)

# Removendo registros duplicados (coordenadas repetidas)
# %%
#mag_sp = mag_sp.drop_duplicates(["decimalLatitude", "decimalLongitude"])

# Coluna Atribuição de quantidade de número de registros para cada espécie
# %%
