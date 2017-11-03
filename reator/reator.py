import pandas as pd
import xlrd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


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

        self.dataframe = pd.read_excel(self.name+'.xlsx', sheetname=numero_planilha,
        skiprows=2, names=cabecalho)

        app = dash.Dash()

        app.layout = html.Div(children=[
        html.H1(children='Dados do Lucena'),
        html.Table([html.Tr([html.Th(col) for col in self.dataframe.columns])] +
        [html.Tr([html.Td(self.dataframe.iloc[i][col]) for col in self.dataframe.columns
        ]) for i in range(len(self.dataframe))]
        )])

        app.run_server()

    def graf_table(self):
        print('Menu das tabelas:')
        lista_planilha = ['R2CA', 'R2SA', 'R4CA', 'R4SA', 'R10CA', 'R10SA',
        'R25CA', 'R25SA']
        for i in range(8):
            print('%i - %s' % (i+1, lista_planilha[i]))
        planilha = int(input("Numero da Planilha: "))-1
        df = self.get_df(planilha)

        app = dash.Dash()

        lista_col = []
        for i in df.columns:
            if "Tempo" not in i:
                if "dados" not in i:
                    lista_col.append({'label': i, 'value': i})

        app.layout = html.Div(
        children=[html.H1(children='Graficos da planilha',
        style={'textAlign': 'center'}),
        html.Div(children='Graficos em linha da planilha %s' % lista_planilha[planilha],
        style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='my-dropdown',
            options=lista_col,
            value='TDH - TDH'
            ),
        dcc.Graph(id='my-graph')
        ])

        @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
        def update_graph(selected_dropdown_value):
            df = self.dataframe
            return {
                'data': [{
                'x': df['Tempo - Data'],
                'y': df[selected_dropdown_value]
                }]
                }
        app.run_server()

    def box_table(self):
        """Esta função acessa todas as tabelas para
        produzir os GraficosBoxPlot."""

        lista_table = ['R2CA', 'R2SA', 'R4CA', 'R4SA', 'R10CA', 'R10SA',
         'R25CA', 'R25SA']
        df = self.get_df(0)
        app = dash.Dash()

        lista_col = []
        for i in df.columns:
            if "Tempo" not in i:
                if "dados" not in i:
                    lista_col.append({'label': i, 'value': i})

        app.layout = html.Div(children=[
        html.H1(children='BoxPlot dos Dados',
        style={
        'textAlign': 'center'
        }),
        html.Div(children="Grafico BoxPlot utilizando todas as tabelas",
        style={
        'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='my-dropdown',
            options=lista_col,
            value='TDH - TDH'
            ),
        dcc.Graph(id='my-graph')
        ])

        @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
        def update_graph(selected_dropdown_value):
            new_df = pd.DataFrame()
            for i in range(8):
                try:
                    new_df[lista_table[i]] = self.get_df(i)[selected_dropdown_value]
                except:
                    select = selected_dropdown_value.split()
                    new_df[lista_table[i]] = self.get_df(i)[' '.join(select)]
            data = []
            for i in new_df.columns:
                data.append({'y': new_df[i], 'name': i, 'type': 'box'})
            return {
            'data': data
        }
        app.run_server()
