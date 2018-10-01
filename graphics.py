from datetime import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Enable the table_schema option in pandas,
# data-explorer makes this snippet available with the `dx` prefix:
pd.options.display.html.table_schema = True
pd.options.display.max_rows = None

jan = {}
jan["2014"] = pd.read_csv('dados/2692_SP_2014_1.csv', delimiter=";", index_col=False)
jan["2016"] = pd.read_csv('dados/2692_SP_2016_1.csv', delimiter=";", index_col=False)
jan["2017"] = pd.read_csv('dados/2692_SP_2017_1.csv', delimiter=";", index_col=False)
jan["2018"] = pd.read_csv('dados/2692_SP_2018_1.csv', delimiter=";", index_col=False)
jan["2014"].head(1)
# codigos das estacoes
codigos = {}
codigos["2014"] = jan["2014"]["codEstacao"].unique()
codigos["2016"] = jan["2016"]["codEstacao"].unique()
codigos["2017"] = jan["2017"]["codEstacao"].unique()
codigos["2018"] = jan["2018"]["codEstacao"].unique()

# ordena dados (datetime e medida), e converte string datahora para tipo datetime
def sortMeasures(data):
    data = data[['datahora','valorMedida']].sort_values(by=['datahora'])
    try:
        times = [datetime.strptime(s[:19], '%d/%m/%Y %H:%M:%S') for s in data["datahora"]]
    except:
        times = [datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S') for s in data["datahora"]]

    measures = data["valorMedida"]

    return times, measures

# compacta os dados para 31 dias
def monthToDays(times, measures):
    gap = int(len(times)/31)
    ftimes = [0]*31
    fmeasures = [0]*31
    for i in range(31):
        ftimes[i] = i+1
        fmeasures[i] = np.sum(map(lambda x: float(x.replace(",",".")), measures[(i*gap):(i*gap+gap if (i*gap+gap < len(times)) else (len(times) - 1))]))

    return ftimes, fmeasures

# calcula dados medios de todos os sensores em um ano (mes do ano)
def yearAvg(year, data):
    year = str(year)
    yearData = {}
    for cod in codigos[year]:
        aux = sortMeasures(data.loc[data["codEstacao"] == cod])
        yearData[cod] = monthToDays(aux[0], aux[1])

    yearFinalTime = range(31)
    yearFinalMeasures = [(np.average([yearData[d][1][i] for d in yearData])) for i in range(31)]
    return (yearFinalTime,yearFinalMeasures)

# calcula media final para cada ano
finalMeasures = [0]*4
i = 0
for year in [2014,2016,2017,2018]:
    finalMeasures[i] = yearAvg(year, jan[str(year)])
    i = i + 1

# get lat long dos sensores
geocodes = jan["2016"][['codEstacao','nomeEstacao','latitude','longitude']].drop_duplicates()
np.average(map(lambda x: float(x.replace(",",".")), geocodes['longitude']))

# plota dados
fig, ax = plt.subplots(4, figsize=(20,16))
plt.xticks(range(0,32))
for j in range(len(finalMeasures)):
    ax[j].plot(finalMeasures[j][0], finalMeasures[j][1])
    ax[j].set_xticks(range(0,32))
    ax[j].set_yticks(range(0,20))
    ax[j].set_title("Janeiro de " + str(2015 + j))
ax[0].set_title("Janeiro de " + str(2014))
plt.show()

fig.savefig("medias.png", dpi=300)

geocodes.loc[geocodes["codEstacao"] == "355030865A"]['latitude'].values[0]
gaugesAvgs = [0]*81
i = 0
for cod in codigos["2016"]:
    gmeasures = map(lambda x: float(x.replace(",",".")), jan["2016"].loc[jan["2016"]["codEstacao"] == cod]['valorMedida'])
    gcodes = geocodes.loc[geocodes["codEstacao"] == cod]
    gaugesAvgs[i] = [gcodes['longitude'].values[0],gcodes['latitude'].values[0], np.average(gmeasures)]
    i = i +1
gaugesAvgs

jan["2016"].loc[jan["2016"]["valorMedida"] > 5].sort_values(by=['valorMedida'], ascending=False)
