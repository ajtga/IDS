import requests
import pandas as pd


def dados_ocorrencia(ano, quantidade=300):
    api = 'http://api.gbif.org/v1/'
    lista_dfs = []
    offset = 0
    iteracoes = int(quantidade/300)
    resto = quantidade % 300
    for i in range(iteracoes):
        ocorrencia = ('occurrence/search?year={}&limit=300&offset={}'.format(ano, offset))
        request = requests.get(api + ocorrencia)
        try:
            lista_dfs.append(pd.DataFrame(request.json()['results']))
        except:
            print('Erro')
        finally:
            offset += 300
    ocorrencia = 'occurrence/search?year={}&limit={}&offset={}'.format(ano, resto, offset)
    request = requests.get(api + ocorrencia)
    try:
        lista_dfs.append(pd.DataFrame(request.json()['results']))
    except:
        print('Erro no ultimo')
    finally:
        df = pd.concat(lista_dfs)
        df.index = df.gbifID
        return df
