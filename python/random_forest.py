import psycopg2
import matplotlib.pyplot as plt
import numpy as np

from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import explained_variance_score

# connect to the PostgreSQL server
conn = psycopg2.connect(host="localhost",database="tcc_development", user="postgres", password="postgres")
# create a cursor
cur = conn.cursor()

cur.execute('SELECT * from global_infos_in_half_hours')
infos_in_half_hours = cur.fetchall()

X = [[int(row[1].strftime("%Y")), int(row[1].strftime("%m")), int(row[1].strftime("%d")), int(row[1].strftime("%H")), int(row[1].strftime("%M")), row[2], row[3], row[4]] for row in infos_in_half_hours[:-1]]
Y = [measure[4] for measure in infos_in_half_hours[1:]]

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

regr = RandomForestRegressor(max_depth=5, random_state=42, n_estimators=50)
regr.fit(X_train, y_train)

y_pred = regr.predict(X_test)
r2_score_lasso = r2_score(y_test, y_pred)
r2_score_lasso

corrects = [((y_test[i] <= 2.5 and y_pred[i] <= 2.5) or (y_test[i] > 2.5 and y_pred[i] > 2.5 and y_test[i] <= 12.5 and y_pred[i] <= 12.5) or (y_test[i] > 12.5 and y_pred[i] > 12.5 and y_test[i] <= 25 and y_pred[i] <= 25) or (y_test[i] > 25 and y_pred[i] > 25)) for i in range(len(y_pred))]
corrects.count(True)
len(corrects)

corrects.count(True)/len(corrects)

explained_variance_score(y_test, y_pred)

all_pred = regr.predict(X)
all_corrects = [((Y[i] <= 2.5 and all_pred[i] <= 2.5) or (Y[i] > 2.5 and all_pred[i] > 2.5 and Y[i] <= 12.5 and all_pred[i] <= 12.5) or (Y[i] > 12.5 and all_pred[i] > 12.5 and Y[i] <= 25 and all_pred[i] <= 25) or (Y[i] > 25 and all_pred[i] > 25)) for i in range(len(all_pred))]
all_corrects.count(True)/len(all_corrects)

all_pred.tofile("allpred.txt", sep="\n")

with open('alltruth.txt', 'w') as f:
    for item in Y:
        f.write("%s\n" % item)

# end connection
cur.close()
conn.close()
