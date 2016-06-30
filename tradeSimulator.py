import pandas as pd
import numpy as np
import sys, random, argparse
import zerodha_option_series as db
import datetime, itertools
import cProfile

def _f (x):
    trade = 0
    if(x['STOCH'] < 0.20):
        trade = 1
    elif(x['STOCH'] > 0.80):
        trade = -1
    return trade

def _generateTrades(testSeries):
    df = testSeries['Data']
    df['STO_HIGH'] = pd.Series.rolling(df['High'], 20, min_periods=20, center=False).max()
    df['STO_LOW'] = pd.Series.rolling(df['Low'], 20, min_periods=20, center=False).min()
    df['STOCH'] = (df['Close'] - df['STO_LOW'])/(df['STO_HIGH'] - df['STO_LOW'])
    df['trades'] = df.apply(_f, axis=1)
    tradeList = df['trades']
    return tradeList


def backtest(testSeries, tradeList):
    df = testSeries['Data']
    df['Holding'] = tradeList
    df['Cash'] = df['Close'] * df['Holding']
    df['Total_Cash'] = df['Cash'].cumsum()
    df['Total_Holding'] = df['Holding'].cumsum()
    df['Total_Value'] = df['Total_Cash'] + df['Total_Holding'] * df['Close']


def main(argv):
    np.set_printoptions(threshold=np.inf)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    args = parser.parse_args()

    conn = db.initDB(args.database)
    cur = conn.cursor()

    testSeries = db.getDictForSeries(cur, 'NIFTY', datetime.datetime(2016, 6, 28, 15, 30), 0, 'FUT')
    tradeList = _generateTrades(testSeries)
    backtest(testSeries, tradeList)
    print testSeries['Data'].tail()

    db.closeDB(conn)
    return 1

if __name__ == '__main__':
    sys.exit(int(main(sys.argv[1:]) or 0))