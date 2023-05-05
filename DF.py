import pandas as pd

com = "ATIMASA S.A."

df = pd.read_excel('DATA_ENTRENAMIENTO.xlsx', sheet_name='Sheet1')

for razon in range(len(df['RAZON'])):
    if df['RAZON'][razon].find(com) != -1:
        print (df['CLASE'][razon])

##print (df)