import pandas as pd
import xlrd
import plotly
import plotly.graph_objs as go
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
        return self.dataframe

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
        print("\n\nSelecione a variavel que sera relacionada:")
        for num, i in enumerate(df.columns):
            print("%d - %s"%(num, i))
            if "Tempo" not in i:
                if "dados" not in i:
                    lista_col.append({'label': i, 'value': i})
        relacao = int(input("Digite o numero referente:"))
        relacao = df.columns[relacao]
        app.layout = html.Div(
        children=[html.H1(children='Graficos da planilha',
        style={'textAlign': 'center'}),
        html.Div(children='Graficos em linha da planilha %s' % lista_planilha[planilha],
        style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='my-dropdown',
            options=lista_col,
            value='Concentração de Glicose (mg/L) - Afluente'
            ),
        dcc.Graph(id='my-graph')
        ])

        @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
        def update_graph(selected_dropdown_value):
            df = self.dataframe.sort_values(by=relacao)
            return {
                'data': [{
                'x': df[relacao],
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

    def graf_uni(self):
        """Multiple Y-Axes"""
        print('Menu das tabelas:')
        lista_planilha = ['R2CA', 'R2SA', 'R4CA', 'R4SA', 'R10CA', 'R10SA',
        'R25CA', 'R25SA']
        for i in range(8):
            print('%i - %s' % (i+1, lista_planilha[i]))
        planilha = int(input("Numero da Planilha: "))-1
        df = self.get_df(planilha)

        relacao = [3, 5, 7, 9, 16, 20]

        data = []
        cont = 2
        flag = True
        cor = ['black', 'red', 'green', 'purple', 'blue', 'brown']
        for num, i in enumerate(df.columns):
            if num in relacao:
                if flag:
                    data.append(go.Scatter(
                    x=df['Tempo - Dia'], y=df[i], name=i,
                    line=dict(color=cor[0])
                    ))
                    flag = False
                else:
                    if i == 'Vol H2 (L) - VH':
                        data.append(go.Scatter(
                        x=df['Tempo - Dia'], y=df[i], name=i,
                        line=dict(color=cor[cont-1], width=4),
                        yaxis=('y'+'%d'%(cont))
                        ))
                        cont += 1
                    else:
                        data.append(go.Scatter(
                        x=df['Tempo - Dia'], y=df[i], name=i,
                        line=dict(color=cor[cont-1]), yaxis=('y'+'%d'%(cont))
                        ))
                        cont += 1

        layout = go.Layout(
        title="Grafico relacionado", xaxis=dict(domain=[0.2, 0.8]),
        yaxis=dict(title='Concentração Glicose', titlefont=dict(color='black'),
        tickfont=dict(color='black')),
        yaxis2=dict(title='DQO', titlefont=dict(color='red'),
        tickfont=dict(color='red'), overlaying='y', anchor='free', side='left',
        position=0),
        yaxis3=dict(title='pH', titlefont=dict(color='green'),
        tickfont=dict(color='green'), overlaying='y', anchor='free',
        side='right', position=0.9),
        yaxis4=dict(title='Acidos Volateis', titlefont=dict(color='purple'),
        tickfont=dict(color='purple'), overlaying='y', anchor='free',
        side='left', position=0.1),
        yaxis5=dict(title='Vol H2', titlefont=dict(color='blue'),
        tickfont=dict(color='blue'), overlaying='y', anchor='free',
        side='right', position=0.8),
        yaxis6=dict(title='mol H2/mol Glicose', titlefont=dict(color='brown'),
        tickfont=dict(color='brown'), overlaying='y', anchor='free',
        side='right', position=1)
        )
        fig = go.Figure(data=data, layout=layout)
        plotly.offline.plot(fig)
