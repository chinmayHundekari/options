import pandas as pd
import numpy as np
import sys, random, argparse
import zerodha_option_series as db
import datetime, itertools
import cProfile
import matplotlib.pyplot as plt

def _f (x):
    trade = 0
    if(x['STOCH'] < 0.20):
        trade = 1
    elif(x['STOCH'] > 0.80):
        trade = -1
    return trade

def _m (x):
    trade = 0
    if(x['MACD_HIST_MOV'] > 0):
        trade = 1
    elif(x['MACD_HIST_MOV'] < 0):
        trade = -1
    return trade

def _r (x):
    trade = 0
    if(x['RSI_MOV'] > 0):
        trade = 1
    elif(x['RSI_MOV'] < 0):
        trade = -1
    return trade

def _generateTrades(testSeries):
    df = testSeries['Data']
    df['STO_HIGH'] = pd.Series.rolling(df['High'], 20, min_periods=20, center=False).max()
    df['STO_LOW'] = pd.Series.rolling(df['Low'], 20, min_periods=20, center=False).min()
    df['STOCH'] = (df['Close'] - df['STO_LOW'])/(df['STO_HIGH'] - df['STO_LOW'])
    df['MA_12'] = pd.Series.rolling(df['Close'], 12, min_periods=12, center=False).mean()
    df['MA_26'] = pd.Series.rolling(df['Close'], 26, min_periods=26, center=False).mean()
    df['MACD'] = df['MA_12'] - df['MA_26']
    df['MACD_9'] = pd.Series.rolling(df['MACD'], 9, min_periods=9, center=False).mean()
    df['MACD_HIST'] = df['MACD'] - df['MACD_9']
    df['MACD_HIST_MOV'] =  1 * (((df['MACD_HIST'].shift(1) - df['MACD_HIST'].shift(2)) > 0) & ((df['MACD_HIST'].shift(1) - df['MACD_HIST'].shift(0)) > 0)) + \
                          -1 * (((df['MACD_HIST'].shift(1) - df['MACD_HIST'].shift(2)) < 0) & ((df['MACD_HIST'].shift(1) - df['MACD_HIST'].shift(0)) < 0)) 
    #df['trades'] = df.apply(_m, axis=1)
    df['RSI_DELTA'] = df['Close'].diff()
    df['RSI_UP'] = df['RSI_DELTA']
    df['RSI_DN'] = df['RSI_DELTA']
    df['RSI_UP'][df['RSI_UP'] < 0] = 0
    df['RSI_DN'][df['RSI_DN'] > 0] = 0
    df['RSI_ROLL_UP'] = pd.Series.rolling(df['RSI_UP'], 14, min_periods=14, center=False).mean()
    df['RSI_ROLL_DN'] = pd.Series.rolling(df['RSI_DN'].abs(), 14, min_periods=14, center=False).mean()
    df['RSI_RS'] = df['RSI_ROLL_UP'] / df['RSI_ROLL_DN']
    df['RSI'] = 100.0 - (100.0 / (1 + df['RSI_RS']))
    #df['RSI'].plot()
    df['RSI_MOV'] = -1 * ((df['RSI'] < 70) & (df['RSI'].shift(1) > 70)) \
                    +1 * ((df['RSI'] > 30) & (df['RSI'].shift(1) < 30))
    df['trades'] = df.apply(_r, axis=1)
    #df.to_csv('calc.csv')
    tradeList = df['trades']
    return tradeList

def _tt(x):
    trade = 0
    if(x['Holding'] != 0):
        trade = 1
    return trade
    
def _CloseAtEOD(x):
    y = pd.to_datetime(x.name).time()
    z = datetime.time(15, 29)
    #print y,z
    if (y == z):
        return -x['Total_Holding']
    else:
        return x['Holding']

def backtest(testSeries, tradeList):
    df = testSeries['Data']
    df['Holding'] = tradeList
    df['Total_Holding'] = df['Holding'].cumsum()
    df['Holding'] = df.apply(_CloseAtEOD, axis=1)
    df['Total_Holding'] = df['Holding'].cumsum()
    df['Cash'] = -1 * df['Close'] * df['Holding']
    df['Total_Cash'] = df['Cash'].cumsum()
    df['Total_Value'] = df['Total_Cash'] + df['Total_Holding'] * df['Close']
    df['Total_Trades'] = df.apply(_tt, axis=1)
    df['Total_Trades'] = df['Total_Trades'].cumsum()
    


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
    testSeries['Data'].to_csv('calc1.csv')
#    plt.plot(list(testSeries['Data']['Total_Value']))
    testSeries['Data']['Total_Value'][0:1000].plot()
    plt.show()
    db.closeDB(conn)
    return 1

if __name__ == '__main__':
    sys.exit(int(main(sys.argv[1:]) or 0))