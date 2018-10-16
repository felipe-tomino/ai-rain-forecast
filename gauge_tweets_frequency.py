from datetime import datetime
import pandas as pd
from geopy import distance

# Enable the table_schema option in pandas,
# data-explorer makes this snippet available with the `dx` prefix:
pd.options.display.html.table_schema = True
pd.options.display.max_rows = None

tweets = pd.read_csv('results/tweetsGauge.csv', delimiter="\t")
relatedAndGauge = tweets[['related','gauge']]

gauges = relatedAndGauge['gauge'].drop_duplicates()

tweetsCount = {}

jan2016 = pd.read_csv('data/rainfall/2692_SP_2016_1.csv', delimiter=";", index_col=False)
gaugesNames = jan2016[['codEstacao','nomeEstacao']].drop_duplicates()

for gauge in gauges:
    gauge_name = gaugesNames.loc[gaugesNames['codEstacao'] == gauge]['nomeEstacao'].values[0]
    subset = relatedAndGauge.loc[relatedAndGauge['gauge'] == gauge]
    # conta quantos tweets tem no sensor, e quantos sao relacionados
    tcnt = subset['gauge'].count()
    relatedcnt = subset.loc[subset['related'] == True]['related'].count()
    tweetsCount[gauge] = [str(gauge_name), str(gauge), tcnt, relatedcnt, (100.*float(relatedcnt)/float(tcnt))]

tweetsCount

maxCount = 0
maxCountGauge = ''
maxRelatedCount = 0
maxRelatedCountGauge = ''

for key, values in tweetsCount.items():
    if values[0] > maxCount:
        maxCount = values[0]
        maxCountGauge = key
    if values[1] > maxRelatedCount:
        maxRelatedCount = values[1]
        maxRelatedCountGauge = key

[maxCount,maxCountGauge,maxRelatedCount,maxRelatedCountGauge]

# sensor '355030833A': 50320 tweets, 123 relacionados
