# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 14:43:37 2017

@author: albuq
"""

#Importando bibliotecas
#%%
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import plotly.plotly as py

#Definindo o diretório
#%%
os.chdir("C:\\Users\\albuq\\OneDrive\\UFAL\\ENGENHARIA_AMBIENTAL_E_SANITÁRIA\\QUINTO_PERIODO\\INTRODUCAO_A_CIENCIA DE DADOS\\CODANDO\\DADOS")

#Importando os dados
#%% #problema algumas linhas #
mag = pd.read_csv("df_novo.zip", compression='zip',sep=";",error_bad_lines=False,low_memory=False)

#Colunas
#%%
mag.columns
colunas=list(mag.columns.values)

#Registros de ocorrência até o nível de espécie
#%%
mag_sp=mag[mag["taxonRank"]=="SPECIES"]
del mag 

#Selecionando colunas 
#%%
mag_sp=mag_sp.loc[:,["gbifID","basisOfRecord","eventDate","year","month","date","stateProvince","municipality","locality","decimalLatitude","decimalLatitude","scientificName","Kingdom","phylum","class","order","family","genus","species"]]

#Ordenado pelos nomes das espécies
#%%
mag_sp.sort_values("species",inplace=True)

###Criando um id para cada espécie
#%%
mag_sp['id'] = mag_sp.groupby("species").ngroup()

#Removendo registros duplicados (coordenadas repetidas)
#%%
mag_sp= mag_sp.drop_duplicates(["decimalLatitude","decimalLongitude"])

#Coluna Atribuição de quantidade de número de registros para cada espécie
#%%