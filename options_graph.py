import json, sys, getopt
import matplotlib.pyplot as plt

keys = {"underlying" : type(u""),
            "underlying_price" : type(1.0),
            "position" : [u"Buy", u"Sell"],
            "volume" : type(1), 
            "strike_price" : type(1),
            "type" : [u"Call",u"Put",u"Future"],
            "expiration_date" : u"dd-mmm-yyyy",
            "price" : type(1.0)}
future_optional_keys = [u"price"]

def plot_graph(xy_ticks, breakeven, breakodd):
    print(xy_ticks, breakeven, breakodd)
    xvals = [tick[0] for tick in xy_ticks]
    yvals = [tick[1] for tick in xy_ticks]
    plt.plot(xvals, yvals)
    plt.axhline(0, color='black')
    xvals = xvals + breakeven + breakodd
    plt.xticks(xvals, rotation=45)
    plt.grid(b=True, which='major', color='g', linestyle='--')
    plt.show()

def validate_json_file(inputfile):
    try:
        ifile = json.load(inputfile)
        #print ifile 
        for contract in ifile['contracts']:
            for keysofkeys in keys:
                if(keysofkeys in contract):
                    if(type(keys[keysofkeys]) == type(type(1))):
                        if(keys[keysofkeys] != type(contract[keysofkeys])):
                            print (keysofkeys, ' not of type', keys[keysofkeys])
                            raise ValueError
                    elif(type(keys[keysofkeys]) == type([1,1])):
                        if((contract[keysofkeys] not in keys[keysofkeys])):
                            print (contract[keysofkeys], 'not in', keys[keysofkeys])
                            raise ValueError
                    elif(type(keys[keysofkeys]) == type(u'')):
                        print (" Not checking for valid dates. Sorry!")
                    else:
                        if(~(contract['type'] == u'Future') & (keysofkeys in future_optional_keys)):
                            print ('Where is this?', keysofkeys)
    except ValueError as e:
        print ('Error loading file!', e)
        return 0
    return ifile

def get_x_ticks(ifile):
    x_ticks = []
    max_val = 0
    min_val = 10000000
    for contract in ifile['contracts']:
        x_ticks.append(contract['strike_price'])
        if(contract['strike_price'] < min_val):
            min_val = contract['strike_price']
        if(contract['strike_price'] > max_val):
            max_val = contract['strike_price']
    if(min_val<10):
        x_ticks.append(min_val - 1)
        x_ticks.append(max_val + 1)
    elif(min_val<100):
        x_ticks.append(min_val - 5)
        x_ticks.append(max_val + 5)
    elif(min_val<1000):
        x_ticks.append(min_val - 50)
        x_ticks.append(max_val + 50)
    elif(min_val<10000):
        x_ticks.append(min_val - 100)
        x_ticks.append(max_val + 100)
    return x_ticks

def processContract(contract, i):
    if contract['position'] == u'Buy':
        if contract['type'] == u'Call':
            if i < contract['strike_price']:
                return -(contract['price'])
            else:
                return (((i - contract['strike_price'])) -(contract['price']))
        elif contract['type'] == u'Put':
            if i > contract['strike_price']:
                return -(contract['price'])
            else:
                return (((contract['strike_price'] - i)) -(contract['price']))
        elif contract['type'] == u'Future':
            return (i - contract['strike_price'])
    elif contract['position'] == u'Sell':
        if contract['type'] == u'Call':
            if i < contract['strike_price']:
                return (contract['price'])
            else:
                return ((contract['price'])) - ((i - contract['strike_price']))
        elif contract['type'] == u'Put':
            if i > contract['strike_price']:
                return (contract['price'])
            else:
                return ((contract['price'])) - ((contract['strike_price'] - i))
        elif contract['type'] == u'Future':
            return (contract['strike_price'] - i)

def convert_json_file(ifile):
    prices = []
    x_ticks = get_x_ticks(ifile)
    xy_ticks = []
    for i in x_ticks:
        sum = 0
        for contract in ifile['contracts']:
            sum = sum + processContract(contract, i)
        xy_ticks.append((i,sum))
        xy_ticks.sort()
        breakeven = []
        breakodd = [] 
        for i in range(0,len(xy_ticks)-1):
            if ((xy_ticks[i][1] < 0) and (xy_ticks[i+1][1] > 0)):
                y1 = xy_ticks[i][1]
                y21 = xy_ticks[i+1][1] - y1
                x1 = xy_ticks[i][0]
                x21 = xy_ticks[i+1][0] - x1
                breakeven.append(-y1 * x21 / y21 + x1)
            elif ((xy_ticks[i][1] > 0) and (xy_ticks[i+1][1] < 0)):
                y1 = xy_ticks[i][1]
                y21 = xy_ticks[i+1][1] - y1
                x1 = xy_ticks[i][0]
                x21 = xy_ticks[i+1][0] - x1
                breakodd.append(-y1 * x21 / y21 + x1)
    return xy_ticks, breakeven, breakodd                

def main(argv):
    inputfile = 'contracts.json'
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('test.py -i <inputfile> -o <outputfile>')
        return -1
    for opt, arg in opts:
        print ('test.py -i <inputfile> -o <outputfile>')
        if opt == '-h':
           sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
       
    contracts = validate_json_file(open(inputfile))
    if(contracts):
        xy_ticks, breakeven, breakodd = convert_json_file(contracts)
    else:
        print ('Invalid json file as input')
        return -1
    if(xy_ticks):
        plot_graph(xy_ticks, breakeven, breakodd)
    else:
        print ('Unable to create a graph. Sorry!')
        return -1
    return 0

if __name__ == '__main__':
    sys.exit(int(main(sys.argv[1:]) or 0))
