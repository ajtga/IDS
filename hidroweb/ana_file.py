import pandas as pd
import zipfile
import io
import plotly
import plotly.graph_objs as go
from datetime import datetime


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
        self.df = super().get_df(self.date_index)
        self.df.drop('Unnamed: 78', axis=1, inplace=True)

    @staticmethod
    def date_index(df):
        df.set_index('Data', inplace=True)
        del (df['Hora'])
        df.sort_index(inplace=True)

    @staticmethod
    def get_days(df, date):
        i = list(df.index)
        days = []
        for day in i:
            days.append(datetime(date.year, date.month, int(day[-2:])))
        return days

    def daily_df(self):
        dates = list(self.df.index)
        dfs = []
        for date in dates:
            flows = self.df.loc[date]['Vazao01':'Vazao31']
            flows.dropna(inplace=True)
            dates = self.get_days(flows, date)
            dfs.append(pd.DataFrame(list(flows), index=dates,
                                    columns=['Vazao']))
        self.daily_flow = pd.concat(dfs, axis=0)

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

        trace0 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 1],
                            y=self.df.Maxima[self.df.NivelConsistencia == 1],
                            name="Raw")
        trace1 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 2],
                            y=self.df.Maxima[self.df.NivelConsistencia == 2],
                            name="Consistent")
        data = [trace0, trace1]
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
