'''
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
  ]
]
'''

OPEN_TIME = 0
OPEN_PRICE = 1
HIGH = 2
LOW = 3
CLOSE_PRICE = 4
VOLUME = 5
CLOSE_TIME = 6
QAV = 7 # QUOTE_ASSET_VOLUME
TRADES = 8 # NUMBER_OF_TRADES
TBBAV = 9 # TAKER_BUY_BASE_ASSET_VOLUME
TBQAV = 10 # TAKER_BUY_QUOTE_ASSET_VOLUME
IGNORE = 11