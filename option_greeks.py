import sys
import argparse
import zerodha_option_series as db
import matplotlib.pyplot as plt
import datetime


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    args = parser.parse_args()

    conn = db.initDB(args.database)
    cur = conn.cursor()
    x = db.getDictForSeries(cur, 'NIFTY', datetime.datetime(2016, 6, 28, 15, 30), 7800, 'CE' )
    
    plt.plot(x['Data']['2016-05-24']['Close'])
    plt.show()
    db.closeDB(conn)
    return 1

if __name__ == '__main__':

    sys.exit(int(main(sys.argv[1:]) or 0))