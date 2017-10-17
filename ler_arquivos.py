
import pandas as pd
import os

def listar_arquivos():
    arquivos = os.listdir(cwd)
    for i in arquivos:
        print("-",i)

def print_lista_tipos():
    print("Os seguintes tipos de arquivos podem ser abertos:")
    print("txt zip csv json html xlsx hdf5 pkl sqlite")    

#escolher pela lista de arquivos
def nome_tipo():
    nome=input("Insira o nome do arquivo que deseja abrir:")
    tipo=input("Insira o seu tipo:")
    #arquivo=int(input("Insira o número do arquivo" ))
    return nome,tipo

def abrir_arquivo(nome,tipo):
    arquivo=nome+"."+tipo
    l=True
    #a="tipo"+"=="+tipo
    if tipo=="txt": #OK
        df=pd.read_csv(arquivo,sep="\t")
    if tipo=="zip": #OK
        df=pd.read_csv(arquivo,sep=";",compression=tipo,skiprows=14)
    if tipo=="csv": #OK
        df=pd.read_csv(arquivo,sep=";")
    if tipo=="json": #+-
        df=pd.read_json(arquivo,lines=True)
        #verificar o tipo de dado de cada coluna. Se for um dicionário,imprimir chaves #problema:lista de dicionarios 
    if tipo=="html": #no
        import lxml
        choice=input("Digite 1 para abrir uma url e 2 para abrir um arquivo local:")
        if choice==1:
           url=input("Insira a url:")
           df=pd.read_html(url)
        else:
            with open(arquivo, 'r') as f:
                df = pd.read_html(f.read())
    if tipo=="xlsx": #ok
        df=pd.ExcelFile(arquivo)
        print(df.sheet_names)
    if tipo=="hdf5": #ok
        import h5py
        df= h5py.File(arquivo,"r")
        #verificando os níveis
        print("Chaves e seus respectivos valores")
        for keys in df.keys():
            print()
            print("-"+keys+":")
            for i in df[str(keys)]:
                print(i)  
    if tipo=="pickle": 
        #df=pd.read_pickle(arquivo)
        import pickle
        with open(arquivo, "rb") as p:
            df = pickle.load(p)
    if tipo=="sql": 
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///arquivo')
        query=input("Escreva a query:")
        with engine.connect() as con:
            #a = con.execute("SELECT * FROM Employee")
            a = con.execute(query)
            df = pd.DataFrame(a.fetchall())
            df.columns = a.keys()
    return df
#main
#definir diretório
try:
    cwd=os.chdir("C:\\Users\\albuq\\OneDrive\\UFAL\\ENGENHARIA_AMBIENTAL_E_SANITÁRIA\\QUINTO_PERIODO\\INTRODUCAO_A_CIENCIA DE DADOS\\CODANDO\\DADOS")
except:
    pass

listar_arquivos()
print_lista_tipos()
nome,tipo=nome_tipo()
dados=abrir_arquivo(nome,tipo)
dados.shape
