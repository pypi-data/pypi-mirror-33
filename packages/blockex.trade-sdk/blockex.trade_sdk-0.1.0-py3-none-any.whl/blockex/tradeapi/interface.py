"""BlockEx Trade API client library"""
from enum import Enum

# default BlockEx production API URL
DEFAULT_API_URL = 'https://api.blockex.com/'
# default BlockEx Markets production API ID
DEFAULT_API_ID = '7c11fb8e-f744-47ee-aec2-9da5eb83ad84'

# HTTP
SUCCESS = 200
BAD_REQUEST = 400
UNAUTHORIZED = 401


class OrderType(Enum):
    """Order types"""
    LIMIT = 'Limit'
    MARKET = 'Market'
    STOP = 'Stop'


class OrderStatus(Enum):
    """Order status int IDs"""
    PENDING = '10'
    FAILED = '15'
    PLACED = '20'
    REJECTED = '30'
    CANCELLED = '40'
    PARTEXECUTED = '50'
    EXECUTED = '60'


class OfferType(Enum):
    """Offer types"""
    BID = 'Bid'
    ASK = 'Ask'


class SortBy(Enum):
    """SortBy types"""
    CURRENCY = "currency"
    DATE = "date"
    PRICE = "price"
    QUANTITY = "quantity"
    TOTAL = "total"


class ApiPath(Enum):
    """Api paths"""
    LOGIN = 'oauth/token'
    LOGOUT = 'oauth/logout'

    GET_TRADER_INFO = 'api/traders/getinfo'
    GET_ORDERS = 'api/orders/get?'
    GET_MARKET_ORDERS = 'api/orders/getMarketOrders?'
    GET_TRADES_HISTORY = 'api/orders/getTradesHistory?'
    CREATE_ORDER = 'api/orders/create?'
    CANCEL_ORDER = 'api/orders/cancel?'
    CANCEL_ALL_ORDERS = 'api/orders/cancelall?'
    GET_TRADER_INSTRUMENTS = 'api/orders/traderinstruments'
    GET_PARTNER_INSTRUMENTS = 'api/orders/partnerinstruments?'
