import pandas as pd
import zipfile
import io
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

class AnaFile:
    
    def __init__(self, file_name):
        with zipfile.ZipFile(file_name + '.zip') as ana_zip:
            with ana_zip.open(file_name + '.txt') as file:
                header_count = 0
                lines = []
                for line in io.TextIOWrapper(file, 'iso8859-1'):
                    if line == '\n':
                        self.header = header_count # saves the number of the line with the header
                    lines.append(line) # saves the lines with informations about the file
                    header_count += 1
                if self.header == None:
                    print('Header end line not found.')
                else: # the part below takes usefull information from the file, such as station code and legend
                    self.head = lines[:self.header]                    
                    head = ''
                    for line in self.head:
                        if len(line)>4 and '//---' not in line:
                            head += line.strip('//') + '\n'
                        if 'Código da Estação' in line:
                            self.station = line.strip('\n').split(':')[-1]
                    self.head = head # saves the informations of the file in self.head, print it and you'll see.
                self.data_type = file_name.lower()
        self.name = file_name
       
    def get_df(self):
        """This method reads a csv file as a pandas DataFrame set the index as
        a datetime index and sets self.df as the DataFrame object.
        Currently ignoring the time column."""

        with zipfile.ZipFile(self.name + '.zip') as ana_zip:
            with ana_zip.open(self.name + '.txt') as file:
                self.df = pd.read_csv(file, header=self.header, sep=';',
                                      decimal=',', encoding='iso8859-1',
                                      parse_dates=['Data'], dayfirst=True)
                self.df.rename(columns={'//EstacaoCodigo':'CodigoEstação'},
                                        inplace=True)
                self.df.index = self.df['Data']
                self.df.sort_index(inplace=True)
                                      
    def save_df(self):
        self.df.to_csv(self.data_type + '_' + self.station)

    # methods for plotting frequently used graphs:
    def plot_line(self):
        """This method plots the graphs of the Dataframe"""
        self.get_df()
        #Plots NivelConsistencia 1 and 2
        trace0=go.Scatter(x=self.df.Data[self.df.NivelConsistencia==1],
                          y=self.df.Maxima[self.df.NivelConsistencia==1],
                          name="Max NC=1")
        trace1=go.Scatter(x=self.df.Data[self.df.NivelConsistencia==2],
                          y=self.df.Maxima[self.df.NivelConsistencia==2],
                          name="Max NC=2")
        data=[trace0,trace1]
        
        layout=dict(title='Estation '+self.station,
                   xaxis=dict(title='Date'),
                   yaxis=dict(title='Data'),
                   )
        plotly.offline.plot({'data':data, 'layout':layout})