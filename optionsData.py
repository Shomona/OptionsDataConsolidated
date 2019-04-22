# load api key
# key this api key private!
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
with open('api_key.txt', 'r') as f:  # equivalent to opening, reading and closing app
    api_key = f.read().replace('\n', '')

# Read from excel into a pandas dataframe
orders = pd.read_csv('flowalgo_all_data_jun_2017_to_feb_2019.csv')
#orders = pd.read_csv('Book1.csv')

# Headers to be passed in the request
headers = {
    "authorization": 'Bearer %s' % api_key,  # for the Traider API
    "accept": 'application/json',
}

endpoint = 'https://sandbox.tradier.com/v1/markets/history'

data_set = []

# Remove all rows with no exact expiration date
orders = orders[orders['EXPIRY'].str.contains('M') == False]

# Convert the expiry column to date time for extraction of year month and day
orders['EXPIRY'] = pd.to_datetime(orders['EXPIRY'])
orders['Date'] = pd.to_datetime(orders['Date'])

# Modify strike to create the symbol
orders['STRIKE'] = orders['STRIKE'] * 1000
orders['STRIKE'] = pd.to_numeric(orders.STRIKE, errors='coerce')
orders = orders[np.isfinite(orders['STRIKE'])]
orders['STRIKE'] = orders.STRIKE.astype(int)

# To calculate the options symbol


def calculate_symbol(row):
    return row['TICKER'] + str(row['EXPIRY'].year % 100) + str(row['EXPIRY'].month).zfill(2) + str(row['EXPIRY'].day).zfill(2) + row['C/P'][0] + str(row['STRIKE']).zfill(8)


orders["SYMBOL"] = orders.apply(calculate_symbol, axis=1)
# To store symbols for filename of excels
symbols = orders["SYMBOL"].tolist()

print(orders);

# Iterate over the pandas dataframe to make requests to the traider api and store the data in a list
for index, row in orders.iterrows():
    #print(str(row['Date'] - timedelta(days=1)))
    params = {
        "symbol": row['SYMBOL'],
        "start": row['Date'] - timedelta(days=1),
        #"start": '2017-06-02',
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data_set.append(response.json())
    else:
        print('error')

print(data_set)
# Used to store the output in dictionary format to easily convert to desired format
output = {"date": [],
          "open": [],
          "close": [],
          "high": [],
          "low": [],
          "volume": [],
          "symbol": [],
          }
index = 0
count = 0

for data in data_set:

    symbol = symbols[count]
    print(symbol)
    try:
        if isinstance(data['history']['day'], list):
            for option in data['history']['day']:
                output['symbol'].append(symbol)
                output['date'].append(option['date'])
                output['open'].append(option['open'])
                output['close'].append(option['close'])
                output['high'].append(option['high'])
                output['low'].append(option['low'])
                output['volume'].append(option['volume'])
    #except Exception as ex:
        #template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #message = template.format(type(ex).__name__, ex.args)
        #print(message)
        else:
            output['symbol'].append(symbol)
            output['date'].append(option['date'])
            output['open'].append(option['open'])
            output['close'].append(option['close'])
            output['high'].append(option['high'])
            output['low'].append(option['low'])
            output['volume'].append(option['volume'])
    except:
        print('Exception occurred')
    count = count + 1

result = pd.DataFrame.from_dict(output)
print(result.shape)
# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('Consolidated_Options_Data.xlsx', engine='xlsxwriter')

result_indexed = result.set_index('symbol')

# Convert the dataframe to an XlsxWriter Excel object.
result_indexed.to_excel(writer, sheet_name='Sheet1')

# Close the Pandas Excel writer and output the Excel file.
writer.save()

#print("The no skipped: " + str(igCount))
