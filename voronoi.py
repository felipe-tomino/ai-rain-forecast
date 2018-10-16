import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

# Enable the table_schema option in pandas,
# data-explorer makes this snippet available with the `dx` prefix:
pd.options.display.html.table_schema = True
pd.options.display.max_rows = None

def commaToFloat(strNumber):
    return float(strNumber.replace(",","."))

jan2016 = pd.read_csv('data/rainfall/2692_SP_2016_1.csv', delimiter=";", index_col=False)
gauges = jan2016[['codEstacao','latitude','longitude']].drop_duplicates()
gauges['latitude'] = gauges['latitude'].map(commaToFloat)
gauges['longitude'] = gauges['longitude'].map(commaToFloat)

voronoi_points = []
for gIndex, gauge in gauges.iterrows():
    voronoi_points.append([gauge['latitude'], gauge['longitude']])

vor = Voronoi(voronoi_points)
fig = voronoi_plot_2d(vor, show_vertices=False)
fig.savefig("voronoi_points.png", dpi=300)

voronoi_points
