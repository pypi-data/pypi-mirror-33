"""1Forge REST API Wrapper"""

from oneforge.version import __version__
from oneforge.client import OneForge


SYMBOLS_MAJOR = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD']
"""Major Forex Pairs"""

SYMBOLS_MINOR = [
    'EURCHF', 'EURGBP', 'EURCAD', 'EURAUD', 'EURNZD', 'EURSEK', 'EURJPY', 'GBPJPY',
    'CHFJPY', 'CADJPY', 'AUDJPY', 'NZDJPY', 'EURNOK', 'GBPCHF', 'GBPAUD', 'GBPCAD',
    'GBPNZD', 'AUDCHF', 'AUDCAD', 'AUDNZD', 'CADCHF', 'NZDCHF', 'NZDCAD'
]
"""Minor Forex Pairs"""

SYMBOLS_CRYPTO = ['BTCUSD', 'ETHUSD', 'LTCUSD', 'XRPUSD']
"""Crypto Pairs"""

SYMBOLS = SYMBOLS_MAJOR + SYMBOLS_MINOR + SYMBOLS_CRYPTO
"""Forex Pairs"""
