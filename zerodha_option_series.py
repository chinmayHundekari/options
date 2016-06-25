import pandas as pd
from glob import glob
import sqlite3
import sys, argparse, os
import csv, re, datetime, time
import matplotlib.pyplot as plt
def monthToNum(shortMonth):
    return{
        'JAN' : 1,
        'FEB' : 2,
        'MAR' : 3,
        'APR' : 4,
        'MAY' : 5,
        'JUN' : 6,
        'JUL' : 7,
        'AUG' : 8,
        'SEP' : 9, 
        'OCT' : 10,
        'NOV' : 11,
        'DEC' : 12
    }[shortMonth]


def initDB(db_file):
   if(os.path.isfile(db_file)):
        conn = sqlite3.connect(db_file)
   else:
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute('CREATE TABLE option_quotes ( \
                Underlying varchar(20), \
                Expiry datetime,    \
                Strike DECIMAL(6,2),    \
                Type varchar(3) NOT NULL CHECK(Type="CE" OR Type="PE" or Type="FUT"),   \
                QTime datetime, \
                Open DECIMAL(5,2) NOT NULL, \
                High DECIMAL(5,2) NOT NULL, \
                Low DECIMAL(5,2) NOT NULL,  \
                Close DECIMAL(5,2) NOT NULL,    \
                Volume INTEGER NOT NULL,    \
                PRIMARY KEY (Underlying, Expiry, Strike, Type, QTime) \
                )')
        except: # OperationalError as e:
            print "Somebody Help! Table exists!!"
            conn = sqlite3.connect(db_file)
   return conn

def closeDB(conn):
    conn.commit()
    conn.close()

def getExpiry(Year, Month):
    return datetime.datetime(int('20' + Year), monthToNum(Month), 28, 15, 30, 0)

def getInfoFromFilename(series):
     basename = os.path.basename(series)
     filename, ext = os.path.splitext(basename)
     if(re.search('FUT',basename)):
         Underlying, Year, Month = re.split(r'(\d+)', filename)
         Month = Month[0:3]
         Strike = 0
         Type = 'FUT'
     else:
         Underlying, Year, Month, Strike, Type = re.split(r'(\d+)', filename)
     Expiry = getExpiry(Year, Month)
     return Underlying, Expiry, Strike, Type     

def storeFile(series, cur):
    quotes = []
    Underlying, Expiry, Strike, Type = getInfoFromFilename(series) 
    with open(series, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        rows = reader.next()
        for row in reader:
            QTime, Open, High, Low, Close, Volume = row
            quotes.append((Underlying, Expiry, Strike, Type, QTime, Open, High,Low, Close, Volume))
        try: 
            cur.executemany('INSERT INTO option_quotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',quotes)
        except sqlite3.IntegrityError as e:
            print ('Data exists for file ' + series + '\n' + e.message)

def getValuesAtTime(cur, Underlying, Expiry, Qtime):
    e = Expiry.strftime('%Y-%m-%d %H:%M:%S')
    qt = Qtime.strftime('%d-%m-%Y %H:%M:%S')
    try:
        cur.execute('SELECT * FROM option_quotes WHERE Underlying=? AND Expiry=? AND QTime=?', (Underlying, e, qt))
    except sqlite3.IntegrityError as e:
        print(e.message)
    return cur.fetchall()

def getValuesForSeries(cur, Underlying, Expiry, Strike, Type):
    e = Expiry.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cur.execute('SELECT * FROM option_quotes WHERE Underlying=? AND Expiry=? AND STRIKE=? AND Type=?', (Underlying, e, Strike, Type))
    except sqlite3.IntegrityError as e:
        print(e.message)
    return cur.fetchall()

def getDictForSeries(cur, Underlying, Expiry, Strike, Type):
    x = getValuesForSeries(cur, Underlying, Expiry, Strike, Type)
    exp = datetime.datetime.strptime(x[0][1], '%Y-%m-%d %H:%M:%S')
    df = pd.DataFrame(x)
    df = df.drop([0,1,2,3], 1)
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    if(Type=='FUT'):
        df['Time'] = pd.to_datetime(df['Time'], format='%d-%m-%Y %H:%M')
    else:
        df['Time'] = pd.to_datetime(df['Time'], format='%d-%m-%Y %H:%M:%S')
    df = df.set_index('Time')
    dic = {'Underlying' : Underlying, 'Expiry' : exp, 'Strike' : Strike, 'Type' : Type, 'Data' : df}
    return dic

def main(argv):
    input_glob = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    parser.add_argument("-i", "--input_glob", nargs='+', help="Input glob for series files")
    args = parser.parse_args()

    conn = initDB(args.database)
    cur = conn.cursor()
    #for in_file in args.input_glob:
    #    storeFile(in_file, cur)
#    x = getValuesAtTime(cur, 'NIFTY', datetime.datetime(2016,6,28, 15, 30) , datetime.datetime(2016,6,24,12,30,0) )
#    x = getValuesForSeries(cur, 'NIFTY', datetime.datetime(2016,6,28, 15, 30), 7800, 'CE' )
    x = getDictForSeries(cur, 'NIFTY', datetime.datetime(2016,6,28, 15, 30), 7800, 'CE' )
#    print x['Data'].dtypes
#    print x['Data']['2016-05-24']
    plt.plot(x['Data']['2016-05-24']['Close'])
    plt.show()
    closeDB(conn)
    return 1

if __name__ == '__main__':

    sys.exit(int(main(sys.argv[1:]) or 0))