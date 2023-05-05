import csv
import pandas as pd

data = []
inicio = 1
total = 0
cont = 0

with open("1704464575_Recibidos.txt") as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"): #You can also use delimiter="\t" rather than giving a dialect.
        if cont >= inicio:
            total += float(line[11])
        cont+=1
total = round(total*0.12,2)    
print (total)
        ##print (line)
        ##data.append(line)
##df = pd.DataFrame(data)
##print(df)