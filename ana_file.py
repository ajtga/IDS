import pandas as pd
import zipfile
import io

class AnaFile:
    
    def __init__(self, file_name):
        with zipfile.ZipFile(file_name + '.zip') as ana_zip:
            with ana_zip.open(file_name + '.txt') as file:
                header_count = 0
                lines = []
                for line in io.TextIOWrapper(file, 'iso8859-1'):
                    if line == '\n':
                        self.header = header_count
                    lines.append(line)
                    header_count += 1
                if self.header == None:
                    print('Header end line not found.')
                else:
                    self.head = lines[:self.header]                    
                    head = ''
                    for line in self.head:
                        if len(line)>4 and '//---' not in line:
                            head += line.strip('//') + '\n'
                        if 'Código da Estação' in line:
                            self.station = line.strip('\n').split(':')[-1]
                    self.head = head
                self.data_type = file_name.lower()
        self.name = file_name
       
    def get_df(self):
        with zipfile.ZipFile(self.name + '.zip') as ana_zip:
            with ana_zip.open(self.name + '.txt') as file:
                self.df = pd.read_csv(file, header=self.header, sep=';',
                                      decimal=',', encoding='iso8859-1',
                                      parse_dates=['Data'], dayfirst=True)
                self.df.rename(columns={'//EstacaoCodigo':'Código da Estação'},
                                        inplace=True)
                self.df.sort_values(by='Data', inplace=True)
                return self.df
                                      
    def save_df(self):
        self.df.to_csv(self.data_type + '_' + self.station)
