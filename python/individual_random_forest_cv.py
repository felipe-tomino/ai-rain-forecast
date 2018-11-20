import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
import errno
# import pickle

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

attribs = [ ["year","month","day","hour","minute","tweets","related","rainfall (mm/30min)","precision","recall"],
            ["hour","minute","tweets","related","rainfall (mm/30min)","precision","recall"],
            ["tweets","related","rainfall (mm/30min)","precision","recall"],
            ["year","month","day","hour","minute","tweets","related","rainfall (mm/30min)"],
            ["hour","minute","tweets","related","rainfall (mm/30min)"],
            ["tweets","related","rainfall (mm/30min)"]]

results_paths = ["./random_forest_regressors_cv/ymdhmtrrpr/",
                "./random_forest_regressors_cv/hmtrrpr/",
                "./random_forest_regressors_cv/trrpr/",
                "./random_forest_regressors_cv/ymdhmtrr/",
                "./random_forest_regressors_cv/hmtrr/",
                "./random_forest_regressors_cv/trr/"]

for attribs_index in range(6):
    if not os.path.exists(os.path.dirname(results_paths[attribs_index])):
        try:
            os.makedirs(os.path.dirname(results_paths[attribs_index]))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    rs = ShuffleSplit(n_splits=10, test_size=.1, random_state=42)

    with open("%srf_scores.csv" %(results_paths[attribs_index]), "w") as scores_file:
        scores_file.write("Sensor;Split;R2 Score;Explained Variance Score;Mesma Classe\n")
        for gauge_id in gauges_ids:
            cur.execute('SELECT * from infos_in_half_hours where gauge_id = %s', [gauge_id])
            infos_in_half_hours = cur.fetchall()

            if (results_paths[attribs_index] == results_paths[0]):
                X = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5], (float(row[4])/241314.0), (float(row[4])/620.0)] for row in infos_in_half_hours[:-1]]
            elif (results_paths[attribs_index] == results_paths[1]):
                X = [[int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5], (float(row[4])/241314.0), (float(row[4])/620.0)] for row in infos_in_half_hours[:-1]]
            elif (results_paths[attribs_index] == results_paths[2]):
                X = [[row[3], row[4], row[5], (float(row[4])/241314.0), (float(row[4])/620.0)] for row in infos_in_half_hours[:-1]]
            elif (results_paths[attribs_index] == results_paths[3]):
                X = [[int(row[2].strftime("%Y")), int(row[2].strftime("%m")), int(row[2].strftime("%d")), int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
            elif (results_paths[attribs_index] == results_paths[4]):
                X = [[int(row[2].strftime("%H")), int(row[2].strftime("%M")), row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]
            elif (results_paths[attribs_index] == results_paths[5]):
                X = [[row[3], row[4], row[5]] for row in infos_in_half_hours[:-1]]

            transformer = MaxAbsScaler().fit(X)
            X_normalized = transformer.transform(X)
            Y = [measure[5] for measure in infos_in_half_hours[1:]]

            regr = RandomForestRegressor(max_depth=5, random_state=42, n_estimators=50)

            split_index = 0
            for train_index, test_index in rs.split(X):
                X_train, X_test, y_train, y_test = split_list(X_normalized,train_index), split_list(X_normalized,test_index), split_list(Y,train_index), split_list(Y,test_index)
                X_original_train, X_original_test = split_list(X,train_index), split_list(X,test_index)

                # pickle.dump(regr, open('./random_forest_regressors_cv/agents/RF_gauge%s_split%s' %(str(gauge_id), split_index), 'wb'))
                regr.fit(X_train, y_train)

                y_pred = regr.predict(X_test)

                r2_score_value = r2_score(y_test, y_pred)
                variance_score = explained_variance_score(y_test, y_pred)

                # http://alertario.rio.rj.gov.br/previsao-do-tempo/termosmet/
                same_class = [((y_test[i] < 2.5 and y_pred[i] < 2.5) or (y_test[i] >= 2.5 and y_pred[i] >= 2.5 and y_test[i] <= 12.5 and y_pred[i] <= 12.5) or (y_test[i] > 12.5 and y_pred[i] > 12.5 and y_test[i] <= 25 and y_pred[i] <= 25) or (y_test[i] > 25 and y_pred[i] > 25)) for i in range(len(y_pred))]
                corrects = same_class.count(True)/len(same_class)

                split_index = split_index + 1

                with open("%sgauge%s_split%s_train.csv" %(results_paths[attribs_index], str(gauge_id), split_index), "w") as f:
                    # print header
                    for attrib in attribs[attribs_index]:
                        f.write("%s;" %(attrib))
                    for attrib in attribs[attribs_index]:
                        f.write("Normalized %s;" %(attrib))
                    f.write("Next batch rainfall (mm/30min)\n")
                    # print data
                    for i in range(len(X_train)):
                        for column in range(len(X_train[i])):
                            f.write("%s;" %(X_original_train[i][column]))
                        for column in range(len(X_train[i])):
                            f.write("%s;" %(X_train[i][column]))
                        f.write("%s\n" %(y_train[i]))

                with open("%sgauge%s_split%s_test.csv" %(results_paths[attribs_index], str(gauge_id), split_index), "w") as f:
                    # print header
                    for attrib in attribs[attribs_index]:
                        f.write("%s;" %(attrib))
                    for attrib in attribs[attribs_index]:
                        f.write("Normalized %s;" %(attrib))
                    f.write("Next batch rainfall (mm/30min);Predicted next batch rainfall (mm/30min);\n")
                    # print data
                    for i in range(len(X_test)):
                        for column in range(len(X_test[i])):
                            f.write("%s;" %(X_original_test[i][column]))
                        for column in range(len(X_test[i])):
                            f.write("%s;" %(X_test[i][column]))
                        f.write("%s;%s\n" %(y_test[i],y_pred[i]))

                scores_file.write("%s;%s;%s;%s;%s\n" %(gauge_id,split_index,r2_score_value,variance_score,corrects))

# end connection
cur.close()
conn.close()
