from enum import Enum, auto


class EnumBase(Enum):
    @classmethod
    def members(cls):
        return set(cls[c] for c in cls.__members__)

    @classmethod
    def names(cls):
        return set(cls[c].name for c in cls.__members__)

    def __lt__(self, other):
        """Used for sorting"""
        return self.name < other.name

class NameEnumMeta(type):
    def __len__(self):
        return self.__len__()

class NameEnum(metaclass=NameEnumMeta):
    @classmethod
    def names(cls):
        return [getattr(cls, k) for k in cls.__dict__.keys() if not k.startswith("__")]

    @classmethod
    def __len__(cls):
        return len(cls.names())

class OHLCVColumn(NameEnum):
    open_time = "open_time"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    returns = "returns"
    funding_rate = "funding_rate"


class SpreadColumn(NameEnum):
    open_time = "open_time"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    returns = "returns"
    zscore = "zscore"


class Instrument(NameEnum):
    """Column names for Exchange active_instruments"""

    instType = "instType"
    symbol = "symbol"
    contract_name = "contract_name"
    listing_date = "listing_date"


class FeeInfo(NameEnum):
    """Column names for Exchange fee info"""

    fee_pct = "fee_pct"
    fee_fixed = "fee_fixed"
    slippage = "slippage"
    init_margin = "init_margin"
    maint_margin = "maint_margin"


class OrderBookSchema(NameEnum):
    "Column Schema for Order Book data structure"

    price = "price"
    """Price of order"""

    quantity = "quantity"
    """Quantity of order"""

    side = "side"
    """See OrderBookSide"""
    
    timestamp = "timestamp"
    """Timestamp of snapshot"""


class OrderBookSide(NameEnum):
    ask = "a"
    bid = "b"

class FundingRateSchema(NameEnum):
    "Column Schema for Funding rate structure"

    timestamp = "timestamp"
    """Timestamp of Funding Rate"""
    
    funding_rate = "fundingRate"
    """Value of Funding Rate """


class Exchange(EnumBase):
    BINANCE = auto()
    BITMEX = auto()
    BYBIT = auto()
    COINFLEX = auto()
    CME = auto()
    FTX = auto()
    OKEX = auto()
    GATEIO = auto()
    KUCOIN = auto()


class InstrumentType(EnumBase):
    PERPETUAL = auto()
    PERP = 1
    QUARTERLY = auto()
    MONTHLY = auto()


class Interval(EnumBase):
    # Global time intervals
    interval_1m = auto()
    interval_3m = auto()
    interval_5m = auto()
    interval_15m = auto()
    interval_30m = auto()
    interval_1h = auto()
    interval_2h = auto()
    interval_4h = auto()
    interval_6h = auto()
    interval_8h = auto()
    interval_12h = auto()
    interval_1d = auto()
    interval_3d = auto()
    interval_1w = auto()


# There is nothing beneath this
class Symbol(EnumBase):
    _1000SHIB = auto()
    _1000XEC = auto()
    _1INCH = auto()
    AAVE = auto()
    ACH = auto()
    ADA = auto()
    AGLD = auto()
    AKRO = auto()
    ALCX = auto()
    ALGO = auto()
    ALICE = auto()
    ALPHA = auto()
    ALT = auto()
    AMPL = auto()
    ANC = auto()
    ANKR = auto()
    ANT = auto()
    AR = auto()
    ARPA = auto()
    ASD = auto()
    ATA = auto()
    ATLAS = auto()
    ATOM = auto()
    AUDIO = auto()
    AVAX = auto()
    AXS = auto()
    BABYDOGE = auto()
    BADGER = auto()
    BAKE = auto()
    BAL = auto()
    BAND = auto()
    BAO = auto()
    BAT = auto()
    BCD = auto()
    BCH = auto()
    BEAM = auto()
    BEL = auto()
    BICO = auto()
    BIT = auto()
    BLZ = auto()
    BNB = auto()
    BNT = auto()
    BOBA = auto()
    BRZ = auto()
    BSV = auto()
    BTC = auto()
    BTCBUSD = auto()
    BTCDOM = auto()
    BTM = auto()
    BTS = auto()
    BTT = auto()
    BZZ = auto()
    C98 = auto()
    CAKE = auto()
    CEL = auto()
    CELO = auto()
    CELR = auto()
    CERE = auto()
    CFX = auto()
    CHR = auto()
    CHZ = auto()
    CKB = auto()
    CLV = auto()
    COMP = auto()
    CONV = auto()
    COTI = auto()
    CQT = auto()
    CREAM = auto()
    CRO = auto()
    CRU = auto()
    CRV = auto()
    CSPR = auto()
    CTK = auto()
    CTSI = auto()
    CUSDT = auto()
    CVC = auto()
    DASH = auto()
    DAWN = auto()
    DEFI = auto()
    DEGO = auto()
    DENT = auto()
    DGB = auto()
    DODO = auto()
    DOGE = auto()
    DORA = auto()
    DOT = auto()
    DRGN = auto()
    DUSK = auto()
    DYDX = auto()
    EDEN = auto()
    EFI = auto()
    EGLD = auto()
    ELON = auto()
    ENJ = auto()
    ENS = auto()
    EOS = auto()
    ETC = auto()
    ETH = auto()
    EXCH = auto()
    FIDA = auto()
    FIL = auto()
    FLEX = auto()
    FLM = auto()
    FLOW = auto()
    FRONT = auto()
    FTM = auto()
    FTT = auto()
    GALA = auto()
    GITCOIN = auto()
    GODS = auto()
    GRIN = auto()
    GRT = auto()
    GTC = auto()
    HBAR = auto()
    HIVE = auto()
    HNT = auto()
    HOLY = auto()
    HOT = auto()
    HT = auto()
    HUM = auto()
    ICP = auto()
    ICX = auto()
    ILV = auto()
    IMX = auto()
    IOST = auto()
    IOTA = auto()
    IOTX = auto()
    IRIS = auto()
    JASMY = auto()
    JST = auto()
    KAVA = auto()
    KEEP = auto()
    KIN = auto()
    KISHU = auto()
    KLAY = auto()
    KNC = auto()
    KSHIB = auto()
    KSM = auto()
    LAT = auto()
    LDO = auto()
    LEO = auto()
    LINA = auto()
    LINK = auto()
    LIT = auto()
    LON = auto()
    LPT = auto()
    LRC = auto()
    LTC = auto()
    LUNA = auto()
    MAKITA = auto()
    MANA = auto()
    MAPS = auto()
    MASK = auto()
    MATIC = auto()
    MBABYDOGE = auto()
    MBOX = auto()
    MCB = auto()
    MEDIA = auto()
    MELON = auto()
    MER = auto()
    MID = auto()
    MINA = auto()
    MIR = auto()
    MKISHU = auto()
    MKR = auto()
    MNGO = auto()
    MOVR = auto()
    MTA = auto()
    MTL = auto()
    MVDA10 = auto()
    MVDA25 = auto()
    NEAR = auto()
    NEO = auto()
    NEST = auto()
    NFT = auto()
    NKN = auto()
    NU = auto()
    OCEAN = auto()
    OGN = auto()
    OKB = auto()
    OMG = auto()
    ONE = auto()
    ONT = auto()
    ORBS = auto()
    OXY = auto()
    PAXG = auto()
    PEARL = auto()
    PEOPLE = auto()
    PERP = auto()
    POLIS = auto()
    POLS = auto()
    POLY = auto()
    POND = auto()
    PRIV = auto()
    PROM = auto()
    PUNDIX = auto()
    QTUM = auto()
    RACA = auto()
    RAD = auto()
    RAMP = auto()
    RAY = auto()
    REEF = auto()
    REN = auto()
    REQ = auto()
    REVV = auto()
    RLC = auto()
    RNDR = auto()
    ROOK = auto()
    ROSE = auto()
    RSR = auto()
    RUNE = auto()
    RVN = auto()
    SAND = auto()
    SC = auto()
    SECO = auto()
    SERO = auto()
    SFP = auto()
    SHIB = auto()
    SHIB1000 = auto()
    SHIT = auto()
    SKL = auto()
    SLP = auto()
    SNX = auto()
    SOL = auto()
    SPELL = auto()
    SRM = auto()
    SRN = auto()
    STARL = auto()
    STEP = auto()
    STMX = auto()
    STORJ = auto()
    STX = auto()
    SUN = auto()
    SUPER = auto()
    SUSHI = auto()
    SWRV = auto()
    SXP = auto()
    TFUEL = auto()
    THETA = auto()
    TLM = auto()
    TOMO = auto()
    TONCOIN = auto()
    TORN = auto()
    TRB = auto()
    TRIBE = auto()
    TRU = auto()
    TRX = auto()
    TRYB = auto()
    TULIP = auto()
    UMA = auto()
    UNFI = auto()
    UNI = auto()
    UNISWAP = auto()
    USDT = auto()
    VET = auto()
    VRA = auto()
    WAVES = auto()
    WAXP = auto()
    WNCG = auto()
    WNXM = auto()
    WOO = auto()
    WSB = auto()
    XAUG = auto()
    XAUT = auto()
    XCH = auto()
    XEC = auto()
    XEM = auto()
    XLM = auto()
    XMR = auto()
    XRP = auto()
    XTZ = auto()
    XVS = auto()
    YFI = auto()
    YFII = auto()
    YGG = auto()
    ZEC = auto()
    ZEN = auto()
    ZIL = auto()
    ZKS = auto()
    ZRX = auto()
