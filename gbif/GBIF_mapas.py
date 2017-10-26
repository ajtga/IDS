import pandas as pd
import os
import plotly as py


# Definindo o diretório
try:
    os.chdir("C:\\Users\\albuq\\OneDrive\\UFAL\\ENGENHARIA_AMBIENTAL_E_SANITÁRIA\\QUINTO_PERIODO\\INTRODUCAO_A_CIENCIA DE DADOS\\CODANDO\\DADOS")
except:
    pass

# Importando os dados #Problemas em algumas linhas
mag = pd.read_csv("df_novo.zip", compression='zip', sep=";", error_bad_lines=False, low_memory=False)

mag.columns
print(list(mag.columns.values))

#Selecionando Registros de ocorrência até o nível de gênero
mag_sp = mag[mag["taxonRank"] == "GENUS"]
del mag

#Selecionando colunas
mag_sp = mag_sp.loc[:, ["gbifID", "basisOfRecord", "eventDate", "year", "month", "date", "stateProvince", "municipality", "locality", "decimalLatitude", "decimalLongitude", "scientificName", "Kingdom", "phylum", "class", "order", "family", "genus"]]

# Criando um id para cada espécie
mag_sp['id'] = mag_sp.groupby("genus").ngroup()

# Removendo registros duplicados
mag_sp = mag_sp.drop_duplicates(["decimalLatitude", "decimalLongitude","genus"])

#Removendo latitudes igual a zero
mag_sp=mag_sp[mag_sp["decimalLatitude"]!="0"]

#Frequência de registros por gênero
mag_sp['freq'] = mag_sp.groupby('genus')['genus'].transform('count')

#Ordenar pela coluna de frequência
mag_sp.sort_values("freq", inplace=True)

#Gerando o mapa

mag_sp['text'] = mag_sp['genus'] + '<br>' +\
    'Estado: '+mag_sp['stateProvince'] + '<br>' +\
    'Data: '+mag_sp['eventDate'].astype(str)


scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

data = [ dict(
        type = 'scattergeo',
        locationmode = 'BRA-states',
        lon = mag_sp['decimalLongitude'],
        lat = mag_sp['decimalLatitude'],
        text = mag_sp['text'],
        mode = 'markers',
        marker = dict(
            size = 8,
            opacity = 0.5,
            reversescale = True,
            autocolorscale = False,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = scl,
            cmin = 1,
            color = mag_sp['freq'],
            cmax = mag_sp['freq'].max(),
            colorbar=dict(
                title="Quantidade de registros de ocorrência por gênero"
            )
        ))]

layout = dict(
        title = 'Registros de ocorrência de Magnoliopsida a nível de gênero',
        colorbar = True,
        geo = dict(
            scope='south america',
            projection=dict( type='equirectangular' ),
            showland = True,
            landcolor = "rgb(200, 200, 200)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 0.5,
            subunitwidth = 0.5
        ),
    )

fig = dict( data=data, layout=layout )
py.offline.plot( fig, validate=False, filename='rg_sp.html' )

