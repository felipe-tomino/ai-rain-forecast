import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
import errno
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import r2_score
from sklearn.metrics import explained_variance_score

def split_list(list, indexes):
    result = []
    for index in indexes:
        result.append(list[index])
    return result

# connect to the PostgreSQL server
conn = psycopg2.connect(host="localhost",database="tcc_development", user="postgres", password="postgres")
# create a cursor
cur = conn.cursor()

cur.execute('SELECT id from gauges')
gauges_ids = [id[0] for id in cur.fetchall()]

all_data = [0]*(np.max(gauges_ids)+1)

rs = ShuffleSplit(n_splits=10, test_size=.1, random_state=42)

rf_results_filename = "./random_forest_regressors_cv/results.csv"
if not os.path.exists(os.path.dirname(rf_results_filename)):
    try:
        os.makedirs(os.path.dirname(rf_results_filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

with open(rf_results_filename, "w") as rf_results_file:
    rf_results_file.write("Gauge ID;Split No;Train Indexes;Test Indexes;Real Y;Predicted Y;Same Class;R2 Score;Explained Variance Score\n")

    for gauge_id in gauges_ids:
        cur.execute('SELECT * from infos_in_half_hours where gauge_id = %s', [gauge_id])
        infos_in_half_hours = cur.fetchall()

        X = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
        transformer = MaxAbsScaler().fit(X)
        X_normalized = transformer.transform(X)
        Y = [measure[5] for measure in infos_in_half_hours[1:]]

        regr = RandomForestRegressor(max_depth=5, random_state=42, n_estimators=50)

        X_norm_filename = "./random_forest_regressors_cv/%s/X_normalized.csv" %(str(gauge_id))
        if not os.path.exists(os.path.dirname(X_norm_filename)):
            try:
                os.makedirs(os.path.dirname(X_norm_filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(X_norm_filename, "w") as f:
            for item in X_normalized.tolist():
                f.write("%s\n" %(item))
        with open("./random_forest_regressors_cv/%s/X.csv" %(str(gauge_id)), "w") as f:
            for item in X:
                f.write("%s\n" %(item))
        with open("./random_forest_regressors_cv/%s/Y.csv" %(str(gauge_id)), "w") as f:
            for item in Y:
                f.write("%s\n" %(item))

        split_index = 0
        for train_index, test_index in rs.split(X):
            X_train, X_test, y_train, y_test = split_list(X,train_index), split_list(X,test_index), split_list(Y,train_index), split_list(Y,test_index)

            pickle.dump(regr, open('./random_forest_regressors_cv/%s/RF_%s' %(str(gauge_id), split_index), 'wb'))
            regr.fit(X_train, y_train)

            y_pred = regr.predict(X_test)

            r2_score_value = r2_score(y_test, y_pred)
            variance_score = explained_variance_score(y_test, y_pred)

            same_class = [((y_test[i] <= 2.5 and y_pred[i] <= 2.5) or (y_test[i] > 2.5 and y_pred[i] > 2.5 and y_test[i] <= 12.5 and y_pred[i] <= 12.5) or (y_test[i] > 12.5 and y_pred[i] > 12.5 and y_test[i] <= 25 and y_pred[i] <= 25) or (y_test[i] > 25 and y_pred[i] > 25)) for i in range(len(y_pred))]
            corrects = same_class.count(True)/len(same_class)

            rf_results_file.write("%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %(gauge_id,split_index,train_index.tolist(),test_index.tolist(),y_test,y_pred.tolist(),corrects,r2_score_value,variance_score))

            split_index = split_index + 1

# end connection
cur.close()
conn.close()
