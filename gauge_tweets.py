from datetime import datetime
import pandas as pd
from geopy import distance
from sys import stdout

# Enable the table_schema option in pandas,
# data-explorer makes this snippet available with the `dx` prefix:
pd.options.display.html.table_schema = True
pd.options.display.max_rows = None

# funcao para converter numero com virgula para float
def commaToFloat(strNumber):
    return float(strNumber.replace(",","."))

# retorna os tweets classificados por sensor
def tweetsCloserGauge(tweetsPos, gaugesPos):
    # dicionario temporario para armazenar sensor de cada id de tweet
    tps = {}

    # para cada tweet
    for tIndex, tweet in tweetsPos.iterrows():
        if (tIndex % 1000 == 0):
            print(tIndex)
        # define o primeiro da lista como mais proximo
        firstGauge = gaugesPos.head(1)
        closestGauge = firstGauge['codEstacao'].values[0]
        minDistance = distance.distance((tweet['x'], tweet['y']), (firstGauge['latitude'].values[0], firstGauge['longitude'].values[0])).km

        # para cada sensor, mede a distancia e a atualiza se for mais proximo
        for gIndex, gauge in gaugesPos.iterrows():
            gDistance = distance.distance((tweet['x'], tweet['y']), (gauge['latitude'], gauge['longitude'])).km
            if (gDistance < minDistance):
                closestGauge = gauge['codEstacao']
                minDistance = gDistance

        # define o sensor mais proximo
        tps[tweet['id_str']] = closestGauge

    # 'mergeia' o dicionario criado e o dataframe de tweets
    final = pd.merge(tweetsPos, pd.DataFrame(list(tps.items()), columns=['id_str','gauge']), on=['id_str'])
    return final

# importa tweets e converte lat long para float
tweets = pd.read_csv('data/AGILE2017/tweets.csv', delimiter=",", index_col=False)
tweets['x'] = tweets['x'].map(commaToFloat)
tweets['y'] = tweets['y'].map(commaToFloat)
# tweets.head(5)

# importa dados dos sensores e converte lat long para float
jan2016 = pd.read_csv('data/rainfall/2692_SP_2016_1.csv', delimiter=";", index_col=False)
gauges = jan2016[['codEstacao','latitude','longitude']].drop_duplicates()
gauges['latitude'] = gauges['latitude'].map(commaToFloat)
gauges['longitude'] = gauges['longitude'].map(commaToFloat)
# gauges.head(5)

# classifica os tweets em relacao aos sensores
classifiedTweets = tweetsCloserGauge(tweets, gauges)
# salva em um arquivo csv
classifiedTweets.to_csv('results/tweetsGauge.csv', sep='\t', encoding='utf-8')
