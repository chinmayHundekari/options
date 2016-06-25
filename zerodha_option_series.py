import pandas as pd
from glob import glob
import sqlite3
import sys, getopt
import argparse

def initDB(db_file):
    if(os.path.isfile(db_file)):
        conn = sqlite3.connect(db_file)
    else:
        c = conn.cursor()
        c.execute('CREATE TABLE quotes (date )
        

    return conn

def closeDB(conn):
    conn.close()


def storeFile(series, cur):
    
    pass

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