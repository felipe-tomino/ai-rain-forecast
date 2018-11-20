import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
import errno
# import pickle

from sklearn.svm import SVR
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import mean_squared_error

def split_list(list, indexes):
    result = []
    for index in indexes:
        result.append(list[index])
    return result

def rain_type(value):
    if (value < 2.5):
        return "fraca"
    elif (value >= 2.5 and value <= 12.5):
        return "moderada"
    elif (value > 12.5 and value <= 25):
        return "forte"
    elif (value > 25):
        return "muito forte"

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

results_paths = ["./SVR_cv_notn/ymdhmtrrpr/",
                "./SVR_cv_notn/hmtrrpr/",
                "./SVR_cv_notn/trrpr/",
                "./SVR_cv_notn/ymdhmtrr/",
                "./SVR_cv_notn/hmtrr/",
                "./SVR_cv_notn/trr/"]

for attribs_index in range(6):
    if not os.path.exists(os.path.dirname(results_paths[attribs_index])):
        try:
            os.makedirs(os.path.dirname(results_paths[attribs_index]))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    rs = ShuffleSplit(n_splits=10, test_size=.1, random_state=42)

    with open("%ssvr_scores.csv" %(results_paths[attribs_index]), "w") as scores_file:
        scores_file.write("Sensor;Split;Mean Squared Error;Accuracy;F1;Recall;Precision\n")
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

            Y = [measure[5] for measure in infos_in_half_hours[1:]]

            regr = SVR(kernel='rbf', C=10, gamma=0.001)

            split_index = 0
            for train_index, test_index in rs.split(X):
                X_train, X_test, y_train, y_test = split_list(X,train_index), split_list(X,test_index), split_list(Y,train_index), split_list(Y,test_index)

                regr.fit(X_train, y_train)

                y_pred = regr.predict(X_test)

                y_train_classified = [rain_type(measure) for measure in y_train]
                y_test_classified = [rain_type(measure) for measure in y_test]
                y_pred_classified = [rain_type(measure) for measure in y_pred]

                # metrics
                mse = mean_squared_error(y_test, y_pred)
                accuracy = accuracy_score(y_test_classified, y_pred_classified)
                f1 = f1_score(y_test_classified, y_pred_classified, average='micro')
                recall = recall_score(y_test_classified, y_pred_classified, average='micro')
                precision = precision_score(y_test_classified, y_pred_classified, average='micro')

                split_index = split_index + 1

                with open("%sgauge%s_split%s_train.csv" %(results_paths[attribs_index], str(gauge_id), split_index), "w") as f:
                    # print header
                    for attrib in attribs[attribs_index]:
                        f.write("%s;" %(attrib))
                    f.write("Next batch rainfall (mm/30min);Next batch rainfall class\n")
                    # print data
                    for i in range(len(X_train)):
                        for column in range(len(X_train[i])):
                            f.write("%s;" %(X_train[i][column]))
                        f.write("%s;%s\n" %(y_train[i], y_train_classified[i]))

                with open("%sgauge%s_split%s_test.csv" %(results_paths[attribs_index], str(gauge_id), split_index), "w") as f:
                    # print header
                    for attrib in attribs[attribs_index]:
                        f.write("%s;" %(attrib))
                    f.write("Next batch rainfall (mm/30min);Predicted next batch rainfall (mm/30min);Next batch rainfall class;Predicted next batch rainfall class\n")
                    # print data
                    for i in range(len(X_test)):
                        for column in range(len(X_test[i])):
                            f.write("%s;" %(X_test[i][column]))
                        f.write("%s;%s;%s;%s\n" %(y_test[i],y_pred[i],y_test_classified[i],y_pred_classified[i]))

                scores_file.write("%s;%s;%s;%s;%s;%s;%s\n" %(gauge_id, split_index, mse, accuracy, f1, recall, precision))

# end connection
cur.close()
conn.close()
