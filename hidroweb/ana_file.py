import math
import numpy as np
import pandas as pd
import zipfile
import io
import plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff
from datetime import timedelta
from calendar import monthrange


class AnaFile:

    def __init__(self, file_name):
        self.name = file_name
        self.station = None
        self.header = None
        self.head = None

        with zipfile.ZipFile(file_name + '.zip') as ana_zip:
            with ana_zip.open(file_name + '.txt') as file:
                header_count = 0
                lines = []
                for line in io.TextIOWrapper(file, 'iso8859-1'):
                    if line == '\n':
                        # saves the number of the line with the header
                        self.header = header_count
                    # saves the lines with information about the file
                    lines.append(line)
                    header_count += 1

                if self.header is None:
                    print('Header not found.')

                # the part below takes useful information from the file,
                # such as station code and legend
                else:
                    self.head = ''
                    head = lines[:self.header]
                    for line in head:
                        if len(line) > 4 and '//---' not in line:
                            self.head += line.strip('//') + '\n'
                        if 'Código da Estação' in line:
                            self.station = int(line.strip('\n').split(':')[-1])

    def __str__(self):
        return self.head

    def get_df(self, set_index):
        """ This method reads a csv file as a pandas DataFrame, sets it's index
        as datetime64 and returns the result. """

        df = pd.read_csv(self.name + '.zip', header=self.header, sep=';',
                         decimal=',', parse_dates=[2], dayfirst=True)
        df.rename(columns={'//EstacaoCodigo': 'EstacaoCodigo'}, inplace=True)
        set_index(df)
        return df


class AnaFlow(AnaFile):

    def __init__(self, file_name):
        super().__init__(file_name)
        self.df = super().get_df(self.multi_index)
        self.df.drop('Unnamed: 78', axis=1, inplace=True)
        self.vazoes_diarias = {}
        self.vazoes_diarias_interpolado = {}
        self.media_vazoes_diarias = {}

        self.__vazao_diaria(1)
        self.__vazao_diaria(2)
        self.__interpolar()
        self.__reduzir_vazoes_diarias()

    @staticmethod
    def multi_index(df):
        if df.Data.duplicated().any():
            print('\nHavia %s data(s) duplicada(s).' % df.Data.duplicated().sum())
        df.rename(columns={'NivelConsistencia': 'Consist.'}, inplace=True)
        df.set_index(['Consist.', 'Data'], inplace=True)
        del df['Hora']
        df.sort_index(inplace=True)

    def __vazao_diaria(self, consistencia):
        nivel_consistencia = (None, 'brutos', 'consistidos')
        try:
            df_vazoes = self.df.loc[consistencia].groupby(self.df.loc[consistencia].index).first()
            datas = list(df_vazoes.index)
            series = []
            for data in datas:
                ultimo_dia = monthrange(data.year, data.month)[1]
                vazoes = df_vazoes.loc[data, 'Vazao01':'Vazao{}'.format(ultimo_dia)]
                datas = [data + timedelta(days=x) for x in range(ultimo_dia)]
                series.append(pd.Series(list(vazoes), index=datas, name='Vazao'))
            self.vazoes_diarias[nivel_consistencia[consistencia]] = pd.concat(series)
        except KeyError:
            print('\nNão há dados {} no DataFrame.\n'.format(nivel_consistencia[consistencia]))

    def relatorio_disponibilidade(self):
        for consistencia in self.vazoes_diarias:
            print(consistencia.upper())
            serie = self.vazoes_diarias[consistencia]
            if serie.hasnans:
                print('\nHá %s valores faltando de um total de %s. Ou seja, %.2f%% dos dados.\n' % (
                      serie.isnull().sum(), len(serie), serie.isnull().sum()/len(serie)*100))

                trace1 = go.Bar(
                    x=['dados'],
                    y=[serie.isnull().sum()],
                    name='Falhas'
                )
                trace2 = go.Bar(
                    x=['dados'],
                    y=[len(serie)],
                    name='Quantidade de dados'
                )
                data = [trace1, trace2]
                layout = go.Layout(
                    barmode='group'
                )
                plotly.offline.plot({'data': data, 'layout': layout})

                try:
                    df = []
                    flag = True
                    frame = serie.to_frame()
                    test = 'test1'
                    for index, i in frame.iterrows():
                        if flag:
                            if not math.isnan(i):
                                flag = False
                                start = index
                        if math.isnan(i):
                            if not flag:
                                flag = True
                                finish = index
                                df.append(dict(Task='Disponibilidade', Start=start,
                                Finish=finish, Resource=test))
                                if test == 'test1':
                                    test = 'test2'
                                else:
                                    test = 'test1'
                    df.append(dict(Task='Disponibilidade', Start=start, Finish=index,
                    Resource=test))

                    colors = {'test1': 'rgb(0, 0, 0)', 'test2': 'rgb(80, 80, 80)'}
                    fig = ff.create_gantt(df, index_col='Resource',
                    group_tasks=True, colors=colors)
                    plotly.offline.plot(fig)
                except:
                    print('Não foi possível obter o gráfico de Gantt para esse conjunto de dados.\n')

                input('Pressione ENTER para continuar.\n')

            else:
                print('\nNão há falhas.\n')

    def __interpolar(self):
        for consistencia in self.vazoes_diarias:
            serie = self.vazoes_diarias[consistencia]
            if not serie.interpolate().hasnans:
                print('\nSucesso na interpolação linear dos dados {}.'.format(consistencia))
                if serie.hasnans:
                    self.vazoes_diarias_interpolado[consistencia] = serie.interpolate()
                else:
                    print('\nFalha na interpolação linear dos dados {}.'.format(consistencia))
            else:
                print('\nNão houve necessidade de interpolação, pois não há (uma quantidade signifivativa?) falhas na série.\n')

    def __reduzir_vazoes_diarias(self):

        def resampler_customizado(array):
            return np.mean(array)

        for consistencia in self.vazoes_diarias_interpolado:
            self.media_vazoes_diarias[consistencia] = self.vazoes_diarias_interpolado[consistencia].resample(
                'M').apply(resampler_customizado)
            print('\nA série com dados {} de vazoes diarias foi reduzida com sucesso.'.format(consistencia))

    def save_df(self):
        options = ('JSON', 'CSV')
        for i, option in enumerate(options):
            print('%s - %s' % (i, option))
        option = int(input('\nChoose an option: '))

        if option == 0:
            self.df.to_json(self.name.lower() + str(self.station) + '.json',
                            date_format='iso')
        elif option == 1:
            self.df.to_csv(self.name.lower() + str(self.station) + '.csv')
        else:
            print('Invalid option. Try again.')

    def plot_line(self):
        """This method plots a line graph of the DataFrame"""

        # Plots 'NivelConsistencia' 1 and 2:
        data = []
        try:
            trace0 = go.Scatter(x=self.df.loc[1].index,
                                y=self.df.loc[1]['Maxima'],
                                name="Raw")
            data.append(trace0)
        except KeyError:
            print('Não há dados brutos no DataFrame.')
        finally:
            trace1 = go.Scatter(x=self.df.loc[2].index,
                                y=self.df.loc[2]['Maxima'],
                                name="Consistent")
            data.append(trace1)
        layout = dict(title='Station ' + str(self.station),
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Maximum Flow (m³/s)'),
                      )
        plotly.offline.plot({'data': data, 'layout': layout})


class AnaRain(AnaFile):

    def __init__(self, file_name):
        super().__init__(file_name)
        self.df = super().get_df(self.date_index)
        self.df.drop('Unnamed: 75', axis=1, inplace=True)

    @staticmethod
    def date_index(df):
        df.set_index('Data', inplace=True)
        df.sort_index(inplace=True)

    def save_df(self):
        options = ('JSON', 'CSV')
        for i, option in enumerate(options):
            print('%s - %s' % (i, option))
        option = int(input('\nChoose an option: '))

        if option == 0:
            self.df.to_json(self.name.lower() + str(self.station) + '.json',
                            date_format='iso')
        elif option == 1:
            self.df.to_csv(self.name.lower() + str(self.station) + '.csv')
        else:
            print('Invalid option. Try again.')

    # Methods for plotting frequently used graphs:
    def plot_line(self):
        """This method plots a line graph of the DataFrame"""

        # Plots 'NivelConsistencia' 1 and 2:

        trace0 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 1],
                            y=self.df.Maxima[self.df.NivelConsistencia == 1],
                            name="Raw")
        trace1 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 2],
                            y=self.df.Maxima[self.df.NivelConsistencia == 2],
                            name="Consistent")
        data = [trace0, trace1]
        layout = dict(title='Station ' + str(self.station),
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Maximum Precipitation (mm)'),
                      )
        plotly.offline.plot({'data': data, 'layout': layout})
