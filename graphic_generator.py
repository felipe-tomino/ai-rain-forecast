from datetime import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Enable the table_schema option in pandas,
# data-explorer makes this snippet available with the `dx` prefix:
pd.options.display.html.table_schema = True
pd.options.display.max_rows = None

codEstacao = '355030833A'

# funcao para converter numero com virgula para float
def commaToFloat(strNumber):
    return float(strNumber.replace(",","."))

jan2016 = pd.read_csv('data/rainfall/2692_SP_2016_1.csv', delimiter=";", index_col=False)
jan2016['datahora'] = pd.to_datetime(jan2016['datahora'])
jan2016 = jan2016.set_index('datahora')
jan2016['valorMedida'] = jan2016['valorMedida'].map(commaToFloat)
gaugeMeasures = jan2016.loc[jan2016['codEstacao'] == codEstacao]

tweetsPerGauge = pd.read_csv('results/tweetsGauge.csv', delimiter="\t", usecols=['created_at', 'related', 'gauge'], index_col=False)
tweetsPerGauge['created_at'] = pd.to_datetime(tweetsPerGauge['created_at'])
tweetsPerGauge = tweetsPerGauge.set_index('created_at')
tweetsOfGauge = tweetsPerGauge.loc[tweetsPerGauge['gauge'] == codEstacao]

day = 01
hour = 0
timestamps = []
tweetsPerTime = []
relatedtweetsPerTime = []
rainfallMeasures = []
for i in range(743):
    startTime = '2016-01-' + str(day) + ' ' + str(hour) + ':00:00'

    if (hour == 23):
        day = day + 1
        hour = 0
    else:
        hour = hour + 1
    endTime = '2016-01-' + str(day) + ' ' + str(hour) + ':00:00'

    timestamps.append(startTime)

    tweetsPerTime.append(tweetsOfGauge.between_time(datetime.time(datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')),
                                                    datetime.time(datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')))['related'].count)
    rainfallMeasures.append(np.sum(gaugeMeasures.between_time(datetime.time(datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')),
                                                              datetime.time(datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')))['valorMedida']))

trange = range(743)
fig, ax = plt.subplots(figsize=(60,16))
ax.plot(trange, rainfallMeasures)
ax.set_title("Chuva Janeiro de 2016. Estacao: 355030833A")
plt.show()


fig, ax = plt.subplots(figsize=(60,16))
ax.plot(timestamps, rainfallMeasures)
ax.set_title("Chuva Janeiro de 2016. Estacao: 355030833A")
plt.show()

# plota dados
fig, ax = plt.subplots(2, figsize=(60,16))
ax[0].plot(timestamps, rainfallMeasures)
ax[0].set_title("Chuva Janeiro de 2016. Estacao: " + str(codEstacao))
ax[1].plot(timestamps, tweetsPerTime)
ax[1].set_title("Tweets Janeiro de 2016. Estacao: " + str(codEstacao))
plt.show()

fig.savefig("medias.png", dpi=300)
