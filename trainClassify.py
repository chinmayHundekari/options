from sklearn.externals.six import StringIO  
import pydot 
import pandas as pd
from matplotlib import style
import numpy as np
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
from sklearn import tree
#from sklearn.neural_network import
from sklearn.externals import joblib
import sqlite3
import sys, argparse, os
import csv, re, datetime, time
import matplotlib.pyplot as plt
import zerodha_option_series as db

def main(argv):
    np.set_printoptions(threshold=np.inf)
    input_glob = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    args = parser.parse_args()

    conn = db.initDB(args.database)
    cur = conn.cursor()

    x = db.getDictForSeries(cur, 'NIFTY', datetime.datetime(2016,6,28, 15, 30), 0, 'FUT' )
    df = x['Data']
    df['PCT_MVMT_1MIN'] = (df['Close'] - df['Close'].shift(+1)) / df['Close'].shift(+1) * 10000
    df['PCT_MVMT_5MIN_POST'] = (df['Close'].shift(-5) - df['Close']) / df['Close'] * 10000
    df['PCT_MVMT_2MIN'] = (df['Close'] - df['Close'].shift(2)) / df['Close'].shift(2) * 10000
    df['PCT_MVMT_5MIN'] = (df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5) * 10000
    df['BUY'] = (df['PCT_MVMT_5MIN_POST'] > 5) * 2 + (df['PCT_MVMT_5MIN_POST'] < -5) * 1 + 0 
    df['STD_DEV'] = pd.Series.rolling(df['Close'], 14, min_periods=14, center=False).std()
    df['BOL_HIGH'] = (df['STD_DEV'] * 2) + pd.Series.rolling(df['Close'], 14, min_periods=14, center=False).mean()
    df['BOL_LOW'] = (df['STD_DEV'] * -2) + pd.Series.rolling(df['Close'], 14, min_periods=14, center=False).mean()
    df['PCT_BOL'] = (df['Close'] - df['BOL_LOW'])/(df['BOL_HIGH'] - df['BOL_LOW'])
    df['STO_HIGH'] = pd.Series.rolling(df['High'], 14, min_periods=14, center=False).max()
    df['STO_LOW'] = pd.Series.rolling(df['Low'], 14, min_periods=14, center=False).min()
    df['STOCH'] = (df['Close'] - df['STO_LOW'])/(df['STO_HIGH'] - df['STO_LOW'])
    df = df[['BUY', 'PCT_MVMT_1MIN' ,'PCT_MVMT_2MIN', 'PCT_MVMT_5MIN', 'PCT_BOL', 'STOCH']]
    #df = df[['BUY', 'PCT_BOL']]

    forecast_col = 'BUY'
    df = df.replace([np.inf, -np.inf], np.nan)
    df.to_csv('calc.csv')
    df.dropna(inplace=True)
    df['label'] = df[forecast_col]
    df = df.drop([forecast_col], 1)

    X = np.array(df.drop(['label'],1))
    #X = preprocessing.scale(X)
    y = np.array(df['label'])
    samples = len(X)
    df.to_csv('calc.csv')
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)
    
    train_filename = datetime.datetime.now().strftime('%Y-%m-d %H:%M:%S') + '.pkl'

    clf = tree.DecisionTreeClassifier()
#    clf = MLPClassifier(algorithm='l-bfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
    clf.fit(X_train, y_train)
#    joblib.dump(clf, train_filename)
    #clf = joblib.load(train_filename) 
    accuracy = clf.score(X_test, y_test)
    print 'Accuracy : ', accuracy
    y_forecast = clf.predict(X_test)
    print 'Total Tests : ', len(y_test), ' Errors : ', sum(y_forecast != y_test)
    print 'Tests for 0: ', sum(y_test == 0), ' Errors : ', sum((y_forecast != y_test)[y_test == 0]) 
    print 'Tests for 1: ', sum(y_test == 1), ' Errors : ', sum((y_forecast != y_test)[y_test == 1])
    print 'Tests for 2: ', sum(y_test == 2), ' Errors : ', sum((y_forecast != y_test)[y_test == 2])
#    dot_data = StringIO() 
#    tree.export_graphviz(clf, out_file=dot_data) 
#    graph = pydot.graph_from_dot_data(dot_data.getvalue()) 
#    graph.write_pdf('a.pdf') 

    db.closeDB(conn)
    return 1

if __name__ == '__main__':

    sys.exit(int(main(sys.argv[1:]) or 0))