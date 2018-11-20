import psycopg2
import matplotlib.pyplot as plt
import numpy as np

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

all_data = [0]*(np.max(gauges_ids)+1)

for gauge_id in gauges_ids:
    cur.execute('SELECT * from infos_in_half_hours where gauge_id = %s', [gauge_id])
    infos_in_half_hours = cur.fetchall()

    X = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
    Y = [measure[5] for measure in infos_in_half_hours[1:]]

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    regr = RandomForestRegressor(max_depth=5, random_state=42, n_estimators=50)
    regr.fit(X_train, y_train)
    pickle.dump(regr, open('./random_forest_regressors/' + str(gauge_id), 'wb'))

    y_pred = regr.predict(X_test)

    r2_score_lasso = r2_score(y_test, y_pred)
    variance_score = explained_variance_score(y_test, y_pred)

    same_class = [((y_test[i] <= 2.5 and y_pred[i] <= 2.5) or (y_test[i] > 2.5 and y_pred[i] > 2.5 and y_test[i] <= 12.5 and y_pred[i] <= 12.5) or (y_test[i] > 12.5 and y_pred[i] > 12.5 and y_test[i] <= 25 and y_pred[i] <= 25) or (y_test[i] > 25 and y_pred[i] > 25)) for i in range(len(y_pred))]
    corrects = same_class.count(True)/len(same_class)

    all_data[gauge_id] = [y_test, y_pred.tolist(), r2_score_lasso, variance_score, corrects]

all_data[0] = ['Real', 'Previsto', 'R2 Score', 'Explained Variance Score', 'Mesma classe']

with open('./results/individual_RF.csv', 'w') as f:
    for item in all_data:
        f.write("%s;%s;%s;%s;%s\n" % (item[0],item[1],item[2],item[3],item[4]))

# end connection
cur.close()
conn.close()
