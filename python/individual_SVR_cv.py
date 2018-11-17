import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
import errno
import pickle

from sklearn.svm import SVR
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

result_path = "./SVR_cv/data/"
if not os.path.exists(os.path.dirname(result_path)):
    try:
        os.makedirs(os.path.dirname(result_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

agents_path = "./SVR_cv/agents/"
if not os.path.exists(os.path.dirname(agents_path)):
    try:
        os.makedirs(os.path.dirname(agents_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

rs = ShuffleSplit(n_splits=10, test_size=.1, random_state=42)

with open("./SVR_cv/data/svr_scores.csv", "w") as scores_file:
    scores_file.write("Sensor;Split;R2 Score;Explained Variance Score;Mesma Classe\n")
    for gauge_id in gauges_ids:
        cur.execute('SELECT * from infos_in_half_hours where gauge_id = %s', [gauge_id])
        infos_in_half_hours = cur.fetchall()

        # X = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
        X = [[int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
        transformer = MaxAbsScaler().fit(X)
        X_normalized = transformer.transform(X)
        Y = [measure[5] for measure in infos_in_half_hours[1:]]

        regr = SVR(kernel='rbf', C=100, gamma=0.001)

        split_index = 0
        for train_index, test_index in rs.split(X):
            X_train, X_test, y_train, y_test = split_list(X_normalized,train_index), split_list(X_normalized,test_index), split_list(Y,train_index), split_list(Y,test_index)
            X_original_train, X_original_test = split_list(X,train_index), split_list(X,test_index)

            pickle.dump(regr, open('./SVR_cv/agents/RF_gauge%s_split%s' %(str(gauge_id), split_index), 'wb'))
            regr.fit(X_train, y_train)

            y_pred = regr.predict(X_test)

            r2_score_value = r2_score(y_test, y_pred)
            variance_score = explained_variance_score(y_test, y_pred)

            # http://alertario.rio.rj.gov.br/previsao-do-tempo/termosmet/
            same_class = [((y_test[i] < 2.5 and y_pred[i] < 2.5) or (y_test[i] >= 2.5 and y_pred[i] >= 2.5 and y_test[i] <= 12.5 and y_pred[i] <= 12.5) or (y_test[i] > 12.5 and y_pred[i] > 12.5 and y_test[i] <= 25 and y_pred[i] <= 25) or (y_test[i] > 25 and y_pred[i] > 25)) for i in range(len(y_pred))]
            corrects = same_class.count(True)/len(same_class)

            split_index = split_index + 1

            with open("./SVR_cv/data/gauge%s_split%s_train.csv" %(str(gauge_id), split_index), "w") as f:
                f.write("Hora;Dia;Total de Tweets;Total de Relacionados;Precipitação (mm/30min);Hora (normalizado);Dia (normalizado);Total de Tweets (normalizado);Total de Relacionados (normalizado);Precipitação (mm/30min) (normalizado); Precipitação para próxima meia hora (mm/30min)")
                for i in range(len(X_train)):
                    f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %(X_original_train[i][0],X_original_train[i][1],X_original_train[i][2],X_original_train[i][3],X_original_train[i][4],X_train[i][0],X_train[i][1],X_train[i][2],X_train[i][3],X_train[i][4],y_train[i]))

            with open("./SVR_cv/data/gauge%s_split%s_test.csv" %(str(gauge_id), split_index), "w") as f:
                f.write("Hora;Dia;Total de Tweets;Total de Relacionados;Precipitação (mm/30min);Hora (normalizado);Dia (normalizado);Total de Tweets (normalizado);Total de Relacionados (normalizado);Precipitação (mm/30min) (normalizado);Precipitação para próxima meia hora (mm/30min);Precipitação Predita para próxima meia hora (mm/30min)")
                for i in range(len(X_test)):
                    f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" %(X_original_test[i][0],X_original_test[i][1],X_original_test[i][2],X_original_test[i][3],X_original_test[i][4],X_test[i][0],X_test[i][1],X_test[i][2],X_test[i][3],X_test[i][4],y_test[i],y_pred[i]))

            scores_file.write("%s;%s;%s;%s;%s\n" %(gauge_id,split_index,r2_score_value,variance_score,corrects))

# end connection
cur.close()
conn.close()
