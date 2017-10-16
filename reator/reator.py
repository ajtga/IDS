import pandas as pd
import xlrd


class Reator:

    def __init__(self, file_name='dados_h2_completo'):
        self.name = file_name
        self.arquivo = xlrd.open_workbook(self.name+'.xlsx')

    def get_df(self, numero_planilha):
        try:
            if numero_planilha < 0:
                print('Numero invalido!')
                return None
            planilha = self.arquivo.sheets()[numero_planilha]
        except:
            if numero_planilha > 7:
                print('Só existem 8 planilhas.')
            return None
        cabecalho = []

        first_line = planilha.row_values(0)
        second_line = planilha.row_values(2)
        for i in range(len(first_line)):
            if first_line[i] != '':
                coluna = first_line[i] + ' - ' + second_line[i]
            else:
                coluna = first_line[i-1] + ' - ' + second_line[i]
            cabecalho.append(coluna)

        dataframe = pd.read_excel(self.name+'.xlsx', sheetname=numero_planilha,
        skiprows=2, names=cabecalho)
        return dataframe
