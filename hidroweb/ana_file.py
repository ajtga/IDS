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
                    print('Header not found.')

                else:  # the part below takes useful information from the file, such as station code and legend
                    self.head = ''
                    head = lines[:self.header]
                    for line in head:
                        if len(line) > 4 and '//---' not in line:
                            self.head += line.strip('//') + '\n'
                        if 'Código da Estação' in line:
                            self.station = int(line.strip('\n').split(':')[-1])
        self.df = self.__get_df()

    def __str__(self):
        return self.head

    def __get_df(self):
        """ This method reads a csv file as a pandas DataFrame, sets it's index as
        datetime64 and returns the result. """

        df = pd.read_csv(self.name + '.zip', header=self.header, sep=';', decimal=',')
        df.rename(columns={'//EstacaoCodigo': 'EstacaoCodigo'}, inplace=True)
        try:
            df.index = pd.to_datetime(df['Data'], dayfirst=True)
            del(df['Hora'], df['Data'])
            df.sort_index(inplace=True)
        except KeyError:
            df.index = pd.to_datetime(df['Data'], dayfirst=True)
            del(df['Data'])
            df.sort_index(inplace=True)

        return df

    def save_df(self):
        options = ('JSON', 'CSV')
        for i, option in enumerate(options):
            print('%s - %s' % (i, option))
        option = int(input('\nChoose an option: '))

        if option == 0:
            self.df.to_json(self.name.lower() + str(self.station) + '.json', date_format='iso')
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
                      yaxis=dict(title='Maximum Flow (m³/s)'),
                      )
        plotly.offline.plot({'data': data, 'layout': layout})
