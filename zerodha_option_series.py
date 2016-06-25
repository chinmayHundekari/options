import pandas as pd
from glob import glob
import sqlite3
import sys, argparse, os
import csv, re, datetime

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
#    if(os.path.isfile(db_file)):
#        conn = sqlite3.connect(db_file)
#    else:
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


def main(argv):
    input_glob = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", nargs='?', default='./db/zerodha_pi.sqlite', help="Database to store series")
    parser.add_argument("-i", "--input_glob", nargs='+', help="Input glob for series files")
    args = parser.parse_args()

    conn = initDB(args.database)
    cur = conn.cursor()
    for in_file in args.input_glob:
        storeFile(in_file, cur)
    closeDB(conn)
    return 1

if __name__ == '__main__':

    sys.exit(int(main(sys.argv[1:]) or 0))