import json, sys, getopt

keys = {"underlying" : type(u""),
            "underlying_price" : type(1.0),
            "position" : [u"Buy", u"Sell"],
            "volume" : type(1), 
            "strike_price" : type(1),
            "type" : [u"Call",u"Put",u"Future"],
            "expiration_date" : u"dd-mmm-yyyy",
            "price" : type(1.0)}
future_optional_keys = [u"strike_price", u"price"]

def plot_graph(contracts):
    pass

def validate_json_file(inputfile):
    try:
        ifile = json.load(inputfile)
        #print ifile 
        for contract in ifile['contracts']:
            for keysofkeys in keys:
                if(keysofkeys in contract):
                    if(type(keys[keysofkeys]) == type(type(1))):
                        if(keys[keysofkeys] != type(contract[keysofkeys])):
                            print keysofkeys, ' not of type', keys[keysofkeys]
                            raise ValueError
                    elif(type(keys[keysofkeys]) == type([1,1])):
                        if((contract[keysofkeys] not in keys[keysofkeys])):
                            print contract[keysofkeys], 'not in', keys[keysofkeys]
                            raise ValueError
                    elif(type(keys[keysofkeys]) == type(u'')):
                        print " Not checking for valid dates. Sorry!"
                    else:
                        if(~(contract['type'] == u'Future') & (keysofkeys in future_optional_keys)):
                            print 'Where is this?', keysofkeys
    except ValueError as e:
        print 'Error loading file!', e
        return 0
    return ifile

def convert_json_file(contracts):
    prices = []
    minVal = 
    for contract in contracts:
        if(contract['type'] == u'Future'):
            if(contract['position'] =u'Buy'):
                
    return prices

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        return -1
    for opt, arg in opts:
        print 'test.py -i <inputfile> -o <outputfile>'
        if opt == '-h':
           sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
       
    contracts = validate_json_file(open(inputfile))
    if(contracts):
        graph_values = convert_json_file(contracts)
    else:
        print 'Invalid json file as input'
        return -1
    if(graph_values):
        plot_graph()
    else:
        print 'Unable to create a graph. Sorry!'
        return -1
    return 0

if __name__ == '__main__':
    sys.exit(int(main(sys.argv[1:]) or 0))
    