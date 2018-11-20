import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
import errno

from sklearn.svm import LinearSVC
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

def split_list(list, indexes):
    result = []
    for index in indexes:
        result.append(list[index])
    return result

def rain_type(value):
    if (value < 2.5):
        return 0
    elif (value >= 2.5 and value <= 12.5):
        return 1
    elif (value > 12.5 and value <= 25):
        return 2
    elif (value > 25):
        return 3

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

results_paths = ["./SVC_cv/ymdhmtrrpr/",
                "./SVC_cv/hmtrrpr/",
                "./SVC_cv/trrpr/",
                "./SVC_cv/ymdhmtrr/",
                "./SVC_cv/hmtrr/",
                "./SVC_cv/trr/"]

gauges_with_one_class = []

for attribs_index in range(6):
    if not os.path.exists(os.path.dirname(results_paths[attribs_index])):
        try:
            os.makedirs(os.path.dirname(results_paths[attribs_index]))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    rs = ShuffleSplit(n_splits=10, test_size=.1, random_state=42)

    with open("%ssvc_scores.csv" %(results_paths[attribs_index]), "w") as scores_file:
        scores_file.write("Sensor;Split;Accuracy;F1;Recall;Precision\n")
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
            Y = [rain_type(measure[5]) for measure in infos_in_half_hours[1:]]

            if len(set(Y)) < 2:
                print("Gauge %s discarded. Set of classes: %s" %(gauge_id, set(Y)))
                gauges_with_one_class.append(gauge_id)
            else:
                print("Gauge %s being used. Set of classes: %s" %(gauge_id, set(Y)))
                split_index = 0
                for train_index, test_index in rs.split(X):
                    split_index = split_index + 1
                    
                    X_train, X_test, y_train, y_test = split_list(X_normalized,train_index), split_list(X_normalized,test_index), split_list(Y,train_index), split_list(Y,test_index)
                    X_original_train, X_original_test = split_list(X,train_index), split_list(X,test_index)

                    if len(set(y_train)) < 2:
                        print("Split %s of cross validation of gauge %s ignored. Set of classes: %s" %(split_index, gauge_id, set(y_train)))
                    else:
                        clf = LinearSVC(random_state=0, tol=1e-5)
                        clf.fit(X_train, y_train)

                        y_pred = clf.predict(X_test)
                        
                        # metrics
                        accuracy = accuracy_score(y_test, y_pred)
                        f1 = f1_score(y_test, y_pred, average='micro')
                        recall = recall_score(y_test, y_pred, average='micro')
                        precision = precision_score(y_test, y_pred, average='micro')


                        with open("%sgauge%s_split%s_train.csv" %(results_paths[attribs_index], str(gauge_id), split_index), "w") as f:
                            # print header
                            for attrib in attribs[attribs_index]:
                                f.write("%s;" %(attrib))
                            for attrib in attribs[attribs_index]:
                                f.write("Normalized %s;" %(attrib))
                            f.write("Next batch rainfall class\n")
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
                            f.write("Next batch rainfall class;Predicted next batch rainfall class\n")
                            # print data
                            for i in range(len(X_test)):
                                for column in range(len(X_test[i])):
                                    f.write("%s;" %(X_original_test[i][column]))
                                for column in range(len(X_test[i])):
                                    f.write("%s;" %(X_test[i][column]))
                                f.write("%s;%s\n" %(y_test[i],y_pred[i]))

                        scores_file.write("%s;%s;%s;%s;%s;%s\n" %(gauge_id, split_index, accuracy, f1, recall, precision))

with open("./SVC_cv/discarded_gauges.csv", "w") as discarded_gauges:
    discarded_gauges.write("%s" %(set(gauges_with_one_class)))

# end connection
cur.close()
conn.close()
