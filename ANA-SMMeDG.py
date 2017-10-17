#Trabalhando com arquivos da ANA para Delmiro Gouveia e São Miguel dos Milagres

#Importando módulos
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

#Definindo diretório
try:
    cwd=os.chdir("C:\\Users\\albuq\\OneDrive\\UFAL\\ENGENHARIA_AMBIENTAL_E_SANITÁRIA\\QUINTO_PERIODO\\INTRODUCAO_A_CIENCIA DE DADOS\\SCRIPTS")
except:
    pass

#Ver arquivos que estão na pasta atual
files = os.listdir(cwd) 
print("Files in '%s': %s" % (cwd, files))

#Importando os arquivos
chuvas_smm = pd.read_csv("CHUVASMM.zip", compression='zip',header=0,skiprows=14,decimal=",",sep=";",parse_dates=True,index_col=["Data"],dayfirst=True)
chuvas_dg= pd.read_csv("CHUVADG.zip", compression='zip', header=0,skiprows=14,decimal=",",sep=";")

#Observando os dados para SMM
chuvas_smm.shape
chuvas_smm.head()
chuvas_smm.tail()
chuvas_smm.columns 
chuvas_smm.info #??
chuvas_smm.describe()
chuvas_smm["Maxima"].describe()
    #Mudar o nome da coluna pelo nome
chuvas_smm=chuvas_smm.rename(columns = {'//EstacaoCodigo':'CodigoEstacao'})

#Observando os dados para DG
chuvas_dg.shape
chuvas_dg.head()
chuvas_dg.tail()
chuvas_dg.columns 
chuvas_dg.info()
chuvas_dg.describe()
chuvas_dg["Maxima"].describe()
    #Mudar o nome da coluna pelo nome
chuvas_dg=chuvas_dg.rename(columns = {'//EstacaoCodigo':'CodigoEstacao'})

#Convertendo para tipo de dado "data"
#chuvas_smm['Data'] = pd.to_datetime(chuvas_smm['Data'],dayfirst=True).values
chuvas_dg['Data'] = pd.to_datetime(chuvas_dg['Data'],dayfirst=True).values
chuvas_dg.index=chuvas_dg["Data"]
chuvas_smm.index.name='data'
chuvas_dg.index.name="data"

#Temos meses que não possem dados, o que fazer? 
#Criar índice novo e reindexar ao data frame
#Tomar o primeiro e o última data
#a=pd.date_range("1/04/1991","1/09/1996",freq="D")
chuvas_dg=chuvas_dg.reindex(pd.date_range("1/04/1991","1/09/1996",freq="D"))
#a=pd.date_range("1/04/1991","1/09/1996",freq="M") #Começa no último dia do mês

#fazer interpolação
chuvas_dg=chuvas_dg.reindex(pd.date_range("1/04/1991","1/09/1996",freq="D")).interpolate(how="polinomial",order=3)
#Fazer resample
    #Média diária
    dg_diaria_media=chuvas_dg.resample("D").mean()
    #Média mensal
    dg_mensal_media=chuvas_dg.resample("M").mean()
    #Média anual

#Plotando a série temporal
chuvas_smm.plot(x='Data', y=['Total', 'Maxima'])
plt.title('Precipitação Total e Máxima - São Miguel dos Milagres')
plt.ylabel('Precipitação (mm)')
plt.show
plt.savefig('Delmiro.png')


chuvas_dg.plot(x='Data', y=['Total', 'Maxima'])
plt.title('Precipitação Total e Máxima - Delmiro Gouveia')
plt.ylabel('Precipitação (mm)')
plt.show
plt.savefig('Delmiro.png')

#Boxplot
chuvas_smm[["Maxima","Total"]].plot(kind="box",subplots=True)
chuvas_dg[["Maxima","Total"]].plot(kind="box",subplots=True)
chuvas_dg[["Maxima","Total"]].plot(kind="bar")






