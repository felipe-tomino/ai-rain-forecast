# este algoritmo cria um regressor random forest por sensor
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import explained_variance_score
import pickle

# connect to the PostgreSQL server
conn = psycopg2.connect(host="localhost",database="tcc_development", user="postgres", password="postgres")
# create a cursor
cur = conn.cursor()

cur.execute('SELECT id from gauges')
gauges_ids = [id[0] for id in cur.fetchall()]

infos_in_half_hours = [0]*(np.max(gauges_ids)+1)
X_train = [0]*(np.max(gauges_ids)+1)
X_test = [0]*(np.max(gauges_ids)+1)
y_train = [0]*(np.max(gauges_ids)+1)
y_test = [0]*(np.max(gauges_ids)+1)
X = [0]*(np.max(gauges_ids)+1)
Y = [0]*(np.max(gauges_ids)+1)
regr = [0]*(np.max(gauges_ids)+1)
y_pred = [0]*(np.max(gauges_ids)+1)
r2_score_lasso = [0]*(np.max(gauges_ids)+1)
corrects = [0]*(np.max(gauges_ids)+1)
variance_score = [0]*(np.max(gauges_ids)+1)
all_data = [0]*(np.max(gauges_ids)+1)

for gauge_id in gauges_ids:
    cur.execute('SELECT * from infos_in_half_hours where gauge_id = %s', [gauge_id])
    infos_in_half_hours[gauge_id] = cur.fetchall()

    X[gauge_id] = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[gauge_id][:-1]]
    Y[gauge_id] = [measure[5] for measure in infos_in_half_hours[gauge_id][1:]]

    X_train[gauge_id], X_test[gauge_id], y_train[gauge_id], y_test[gauge_id] = train_test_split(X[gauge_id], Y[gauge_id], test_size=0.2, random_state=42)

    regr[gauge_id] = RandomForestRegressor(max_depth=5, random_state=42, n_estimators=50)
    regr[gauge_id].fit(X_train[gauge_id], y_train[gauge_id])
    pickle.dump(regr[gauge_id], open('./random_forest_regressors/' + str(gauge_id), 'wb'))

    y_pred[gauge_id] = regr[gauge_id].predict(X_test[gauge_id])

    r2_score_lasso[gauge_id] = r2_score(y_test[gauge_id], y_pred[gauge_id])
    variance_score[gauge_id] = explained_variance_score(y_test[gauge_id], y_pred[gauge_id])

    same_class = [((y_test[gauge_id][i] <= 2.5 and y_pred[gauge_id][i] <= 2.5) or (y_test[gauge_id][i] > 2.5 and y_pred[gauge_id][i] > 2.5 and y_test[gauge_id][i] <= 12.5 and y_pred[gauge_id][i] <= 12.5) or (y_test[gauge_id][i] > 12.5 and y_pred[gauge_id][i] > 12.5 and y_test[gauge_id][i] <= 25 and y_pred[gauge_id][i] <= 25) or (y_test[gauge_id][i] > 25 and y_pred[gauge_id][i] > 25)) for i in range(len(y_pred[gauge_id]))]
    corrects[gauge_id] = same_class.count(True)/len(same_class)

    all_data[gauge_id] = [y_test[gauge_id], y_pred[gauge_id].tolist(), r2_score_lasso[gauge_id], variance_score[gauge_id], corrects[gauge_id]]

all_data[0] = ['Real', 'Previsto', 'R2 Score', 'Explained Variance Score', 'Mesma classe']

with open('./results/individual_RF.csv', 'w') as f:
    for item in all_data:
        f.write("%s;%s;%s;%s;%s\n" % (item[0],item[1],item[2],item[3],item[4]))

# end connection
cur.close()
conn.close()
