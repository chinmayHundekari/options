import sys
import argparse
import zerodha_option_series as db
import matplotlib.pyplot as plt
import datetime
import optionGreeks

def _iv(x):
    iv = 0
    return iv

def addGreeksToSeries(series):
    df = series['Data']
    df['IV'] = df.apply(_iv, axis=1, args=())  
    df['delta'] = 
    df['theta'] = 
    df['vega'] = 


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    parser.add_argument("-i", "--interest", nargs='?', default='7.00', help="Risk Free interest rate")
    args = parser.parse_args()

    conn = db.initDB(args.database)
    cur = conn.cursor()
    x = db.getDictForSeries(cur, 'NIFTY', datetime.datetime(2016, 6, 28, 15, 30), 7800, 'CE' )
    addGreeksToSeries(x)
    plt.plot(x['Data']['2016-05-24']['Close'])
    plt.show()
    db.closeDB(conn)
    return 1

if __name__ == '__main__':

    sys.exit(int(main(sys.argv[1:]) or 0))