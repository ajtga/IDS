import pandas as pd
import zipfile
import io
import plotly
import plotly.plotly as py
import plotly.graph_objs as go


class AnaFile:

    def __init__(self, file_name):
        self.name = file_name
        self.station = None
        self.header = None
        self.head = None
        self.df = None

        with zipfile.ZipFile(file_name + '.zip') as ana_zip:
            with ana_zip.open(file_name + '.txt') as file:
                header_count = 0
                lines = []
                for line in io.TextIOWrapper(file, 'iso8859-1'):
                    if line == '\n':
                        self.header = header_count  # saves the number of the line with the header
                    lines.append(line)  # saves the lines with information about the file
                    header_count += 1

                if self.header is None:
                    print('Header end line not found.')

                else:  # the part below takes useful information from the file, such as station code and legend
                    self.head = ''
                    head = lines[:self.header]
                    for line in head:
                        if len(line) > 4 and '//---' not in line:
                            self.head += line.strip('//') + '\n'
                        if 'Código da Estação' in line:
                            self.station = line.strip('\n').split(':')[-1]

    @staticmethod
    def concat_datetime(row):
        """ This method takes str from 'Data' and 'Hora', then concatenate and returns it."""

        # CAN parse_dates DO THE SAME WHEN COMBINING COLUMNS?
        return row['Data'] + ' ' + row['Hora'][-8:]

    def get_df(self):
        """This method reads a csv file as a pandas DataFrame set the index as
        a datetime index and sets self.df as the DataFrame object.
        Currently ignoring the time column."""

        self.df = pd.read_csv(self.name + '.zip', header=self.header, sep=';', decimal=',')
        self.df.rename(columns={'//EstacaoCodigo': 'CodigoEstação'},
                       inplace=True)
        if not pd.isnull(self.df['Hora']).all():  # treat exceptions
            self.df['Datetime'] = self.df.apply(self.concat_datetime, axis=1)
            self.df.index = pd.to_datetime(self.df['Datetime'], dayfirst=True)
            del (self.df['Datetime'], self.df['Data'], self.df['Hora'])
            self.df.sort_index(inplace=True)
        else:
            self.df.index = list(pd.to_datetime(self.df['Data'], dayfirst=True))
            del(self.df['Hora'], self.df['Data'])
            self.df.sort_index(inplace=True)

    def save_df(self):
        self.df.to_csv(self.name.lower() + '_' + self.station)

    # Methods for plotting frequently used graphs:
    def plot_line(self):
        """This method plots a line graph of the DataFrame"""

        self.get_df()

        # Plots 'NivelConsistencia' 1 and 2:

        trace0 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 1],
                            y=self.df.Maxima[self.df.NivelConsistencia == 1],
                            name="Max NC=1")
        trace1 = go.Scatter(x=self.df.index[self.df.NivelConsistencia == 2],
                            y=self.df.Maxima[self.df.NivelConsistencia == 2],
                            name="Max NC=2")
        data = [trace0, trace1]
        layout = dict(title='Station '+self.station,
                      xaxis=dict(title='Date'),
                      yaxis=dict(title='Data'),
                      )
        plotly.offline.plot({'data': data, 'layout': layout})
