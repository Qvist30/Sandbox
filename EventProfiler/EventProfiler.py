'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv
import matplotlib.pyplot as plt


"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, bollingerVals):
##    ''' Finding the event dataframe '''
##    df_close = bollinger['close']
##    ts_market = df_close['SPY']
##
    print "Finding Events"
##
##    # Creating an empty dataframe
    df_events = copy.deepcopy(bollingerVals)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = bollingerVals.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            if bollingerVals[s_sym][i] <= -2 and bollingerVals[s_sym][i -1 ] >= -2 and bollingerVals['SPY'][i] >= 1:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

def updateValues(trades, todaysDate, cash, ownedStocks, na_price, day):
    value = 0
    for i in range(0, len(trades)):
        if todaysDate.year == trades[i]['year'] and todaysDate.month == trades[i]['month'] and todaysDate.day == trades[i]['day']:
            value, ownedStocks, cash = updateOwnedStocks(cash, trades[i], ownedStocks, todaysDate, na_price, day)
    for ownedStock in ownedStocks:
##        print value
##        print ownedStock['shares']
##        print na_price[ownedStock['symbol']][day]
        value = value+ ownedStock['shares'] * na_price[ownedStock['symbol']][day]
    return value, cash, ownedStocks

def updateOwnedStocks(cash, trade, ownedStocks, todaysDate, na_price, day):
##    print trade['ordertype']
    value = 0
    if trade['ordertype'] == 'Buy':
        cash = cash - (na_price[trade['symbol']][day] * trade['shares'])
        for ownedStock in ownedStocks:
            if trade['symbol'] == ownedStock['symbol']:
                ownedStock['shares'] = ownedStock['shares'] + trade['shares']
            
    else:
        cash = cash + (na_price[trade['symbol']][day] * trade['shares'])
        for ownedStock in ownedStocks:
            if trade['symbol'] == ownedStock['symbol']:
                ownedStock['shares'] = ownedStock['shares'] - trade['shares']
            
    return value, ownedStocks, cash
def analyze(valuesFile):
    symbols = ['/$SPX']
    benchmark = '/$SPX'
    values = np.loadtxt(valuesFile, delimiter=',', dtype = [('year', int), ('month', int), ('day', int),('value', int)])
    dt_start = dt.datetime(values['year'][0], values['month'][0], values['day'][0])
    dt_end = dt.datetime(values['year'][len(values)-1], values['month'][len(values)-1], values['day'][len(values)-1] +1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dailyValuesOnly = values['value']
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    benchmarkPrices = d_data['close'].values
    na_price = np.zeros(shape=(len(ldt_timestamps), 2))
    dailyAverage = np.zeros(shape=len(ldt_timestamps))
    benchmarkAverage = np.zeros(shape=len(ldt_timestamps))
    for i in range(0,len(ldt_timestamps)):
        na_price[i] = (dailyValuesOnly[i], benchmarkPrices[i])
        if i!=0:
            dailyAverage[i] = na_price[i][0] / na_price[i-1][0] -1
            benchmarkAverage[i] = na_price[i][1] / na_price[i-1][1] -1
    na_normalized_price = np.zeros(shape=(len(ldt_timestamps), 2))
    na_normalized_price = na_price / na_price[0, :]
    plt.clf()
    plt.plot(ldt_timestamps, na_normalized_price)
    plt.legend(['Portfolio Value', benchmark])
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('homework7.pdf', format='pdf')
    print
    print "Standard Deviation of Fund: " + str(np.std(dailyAverage))
    print "Standard Deviation of " + benchmark + ": " + str(np.std(benchmarkAverage))

    print "Average Return of Fund: " + str(np.average(dailyAverage))
    print "Standard Deviation of " + benchmark + ": " + str(np.average(benchmarkAverage))

    sharpeFund = np.sqrt(252) * (np.average(dailyAverage)/np.std(dailyAverage))
    sharpeBenchmark = np.sqrt(252) * (np.average(benchmarkAverage)/np.std(benchmarkAverage))

    print "Sharpe Ratio of Fund: " + str(sharpeFund)
    print "Sharpe Ratio of " + benchmark + ": " + str(sharpeBenchmark)

    print "Cumulative Return of Fund: " + str(na_normalized_price[len(ldt_timestamps) -1][0])
    print "Cumulative Return of Benchmark: " + str(na_normalized_price[len(ldt_timestamps) -1][1])

def simulate(startingValue, ordersFile):
    ##with open(ordersFile, 'wb') as csvfile:
    trades = np.loadtxt(ordersFile, delimiter=',', dtype = [('year', int), ('month', int), ('day', int),('symbol', 'S10'), ('ordertype', 'S10'), ('shares', int)])
    
    trades.sort(order=['year', 'month', 'day'], axis=0)
    dt_start = dt.datetime(trades['year'][0], trades['month'][0], trades['day'][0])
    dt_end = dt.datetime(trades['year'][len(trades)-1], trades['month'][len(trades)-1], trades['day'][len(trades)-1] +1)
    symbols = np.unique(trades['symbol'])
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    dailyValue = np.zeros((len(ldt_timestamps), 4), dtype='int')
    ownedStocks = np.zeros((len(symbols)),dtype=[('symbol', 'S10'),('shares', int)])
    ownedStocks['symbol'] = symbols.reshape(1,len(symbols))
    na_price = d_data['close']
    na_price = na_price.fillna(method = 'ffill')
    na_price = na_price.fillna(method='backfill')
##    print na_price[symbols[0]]
    cash = int(startingValue)
    for i in range(0, len(ldt_timestamps)):
        todaysValue, cash, ownedStocks = updateValues(trades, ldt_timestamps[i], cash, ownedStocks, na_price, i)
##        print todaysValue
##        print cash
        dailyValue[i] = (ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day, cash + todaysValue)
    valuesFileName = 'homework7dailyvalues.csv'
    with open(valuesFileName, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for value in dailyValue:
            spamwriter.writerow(value)
    return valuesFileName

if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list('sp5002012')
    symbols.append('SPY')
    adjcloses = dataobj.get_data(ldt_timestamps, symbols, "close")
    actualclose = dataobj.get_data(ldt_timestamps, symbols, "actual_close")

    adjcloses = adjcloses.fillna(method = 'ffill')
    adjcloses = adjcloses.fillna(method='backfill')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    means = pd.rolling_mean(adjcloses, 20, min_periods=20)
    stds = pd.rolling_std(adjcloses, 20, min_periods=20)
    bollinger_val = means.copy(deep=True)
##    print (adjcloses[symbols[0]][0] - means[symbols[0]][0]) / stds[symbols[0]][0]
    upperValue = means.copy(deep=True)
    lowerValue = means.copy(deep=True)
##    df_events = copy.deepcopy(bollinger_val)
##    df_events = df_events * np.NAN
    counter = 0
    for j in range(len(ldt_timestamps)):
        bollinger_val['SPY'][j] = (adjcloses['SPY'][j] - means['SPY'][j]) / stds['SPY'][j]  
    tradesFileName = 'homework7trades.csv'
    with open(tradesFileName, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for i in range(len(symbols)):
            for j in range(len(ldt_timestamps)):

##            upperValue[symbols[i]][j] = means[symbols[i]][j] + stds[symbols[i]][j]
##            lowerValue[symbols[i]][j] = means[symbols[i]][j] - stds[symbols[i]][j]
                bollinger_val[symbols[i]][j] = (adjcloses[symbols[i]][j] - means[symbols[i]][j]) / stds[symbols[i]][j]
##                if bollinger_val[symbols[i]][j] < -2 and bollinger_val[symbols[i]][j - 1] >= -2 and bollinger_val['SPY'][j] >= 1.5:
                if adjcloses[symbols[i]][j] < adjcloses[symbols[i]][j-1] * .95:
                    numShares = 1000 / adjcloses[symbols[i]][j]
                    spamwriter.writerow([ldt_timestamps[j].year, ldt_timestamps[j].month, ldt_timestamps[j].day, symbols[i], 'Buy', numShares] )
                    if j < len(ldt_timestamps) -5:
                        spamwriter.writerow([ldt_timestamps[j + 5].year, ldt_timestamps[j + 5].month, ldt_timestamps[j + 5].day, symbols[i], 'Sell', numShares] )
                    else:
                        spamwriter.writerow([ldt_timestamps[len(ldt_timestamps) -1].year, ldt_timestamps[len(ldt_timestamps) -1].month, ldt_timestamps[len(ldt_timestamps) -1].day, symbols[i], 'Sell', numShares] )
                    counter = counter +1
                    print counter;
    portfolioValue = simulate(50000, tradesFileName)
    analyze(portfolioValue)
##    df_events = find_events(symbols, bollinger_val)
##    print "Creating Study"
##    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
##                s_filename='homework7.pdf', b_market_neutral=False, b_errorbars=True,
##                s_market_sym='SPY')
