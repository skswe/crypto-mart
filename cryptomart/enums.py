from pyutil.enums import NameEnum


class OHLCVColumn(NameEnum):
    "Column names for OHLCV data feed"

    open_time = "open_time"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    returns = "returns"


class Instrument(NameEnum):
    """Column names for Exchange active_instruments"""

    symbol = "symbol"
    instType = "instType"
    contract_name = "contract_name"
    listing_date = "listing_date"


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
    """Possible values for OrderBookSchema.side"""

    ask = "a"
    bid = "b"


class Exchange(NameEnum):
    """Names of registered exchanges in the API"""

    BINANCE = "binance"
    BITMEX = "bitmex"
    BYBIT = "bybit"
    COINFLEX = "coinflex"
    FTX = "ftx"
    OKEX = "okex"
    GATEIO = "gateio"
    KUCOIN = "kucoin"


class InstrumentType(NameEnum):
    """Names of registered instrument types in the API"""

    PERPETUAL = "perpetual"
    PERP = "perpetual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    SPOT = "spot"


class Interval(NameEnum):
    """Names of registered historical candlestick data intervals in the API"""

    interval_1m = "interval_1m"
    interval_3m = "interval_3m"
    interval_5m = "interval_5m"
    interval_15m = "interval_15m"
    interval_30m = "interval_30m"
    interval_1h = "interval_1h"
    interval_2h = "interval_2h"
    interval_4h = "interval_4h"
    interval_6h = "interval_6h"
    interval_8h = "interval_8h"
    interval_12h = "interval_12h"
    interval_1d = "interval_1d"
    interval_3d = "interval_3d"
    interval_1w = "interval_1w"


class Symbol(NameEnum):
    """Names of registered symbols in the API"""

    _10000NFT = "_10000NFT"
    _1000BTT = "_1000BTT"
    _1000SHIB = "_1000SHIB"
    _1000XEC = "_1000XEC"
    _10SET = "_10SET"
    _1ART = "_1ART"
    _1EARTH = "_1EARTH"
    _1INCH = "_1INCH"
    _1INCH3L = "_1INCH3L"
    _1INCH3S = "_1INCH3S"
    _2CRZ = "_2CRZ"
    _88MPH = "_88MPH"
    A5T = "A5T"
    AAA = "AAA"
    AAC = "AAC"
    AAG = "AAG"
    AART = "AART"
    AAVE = "AAVE"
    AAVE3L = "AAVE3L"
    AAVE3S = "AAVE3S"
    ABBC = "ABBC"
    ABT = "ABT"
    ACA = "ACA"
    ACE = "ACE"
    ACH = "ACH"
    ACH3L = "ACH3L"
    ACH3S = "ACH3S"
    ACM = "ACM"
    ACOIN = "ACOIN"
    ACT = "ACT"
    ADA = "ADA"
    ADA3L = "ADA3L"
    ADA3S = "ADA3S"
    ADADOWN = "ADADOWN"
    ADAPAD = "ADAPAD"
    ADAUP = "ADAUP"
    ADEL = "ADEL"
    ADP = "ADP"
    ADS = "ADS"
    ADX = "ADX"
    AE = "AE"
    AERGO = "AERGO"
    AFC = "AFC"
    AFK = "AFK"
    AGIX = "AGIX"
    AGLD = "AGLD"
    AGS = "AGS"
    AI = "AI"
    AION = "AION"
    AIOZ = "AIOZ"
    AIR = "AIR"
    AKITA = "AKITA"
    AKRO = "AKRO"
    AKT = "AKT"
    ALAYA = "ALAYA"
    ALBT = "ALBT"
    ALCX = "ALCX"
    ALD = "ALD"
    ALEPH = "ALEPH"
    ALGO = "ALGO"
    ALGO3L = "ALGO3L"
    ALGO3S = "ALGO3S"
    ALICE = "ALICE"
    ALICE3L = "ALICE3L"
    ALICE3S = "ALICE3S"
    ALN = "ALN"
    ALPA = "ALPA"
    ALPACA = "ALPACA"
    ALPH = "ALPH"
    ALPHA = "ALPHA"
    ALPHA3L = "ALPHA3L"
    ALPHA3S = "ALPHA3S"
    ALPHR = "ALPHR"
    ALPINE = "ALPINE"
    ALT = "ALT"
    ALTB = "ALTB"
    ALTMEXT = "ALTMEXT"
    ALU = "ALU"
    ALV = "ALV"
    ALY = "ALY"
    AME = "AME"
    AMP = "AMP"
    AMPL = "AMPL"
    AMPL3L = "AMPL3L"
    AMPL3S = "AMPL3S"
    ANC = "ANC"
    ANC3L = "ANC3L"
    ANC3S = "ANC3S"
    ANGLE = "ANGLE"
    ANKR = "ANKR"
    ANML = "ANML"
    ANT = "ANT"
    ANW = "ANW"
    AOA = "AOA"
    AOG = "AOG"
    APE = "APE"
    APE3L = "APE3L"
    APE3S = "APE3S"
    API3 = "API3"
    API33L = "API33L"
    API33S = "API33S"
    APIX = "APIX"
    APL = "APL"
    APM = "APM"
    APN = "APN"
    APT = "APT"
    APX = "APX"
    APYS = "APYS"
    AQT = "AQT"
    AR = "AR"
    AR3L = "AR3L"
    AR3S = "AR3S"
    ARCX = "ARCX"
    ARDR = "ARDR"
    ARES = "ARES"
    ARGON = "ARGON"
    ARK = "ARK"
    ARKER = "ARKER"
    ARMOR = "ARMOR"
    ARNM = "ARNM"
    ARNX = "ARNX"
    ARPA = "ARPA"
    ARPA3L = "ARPA3L"
    ARPA3S = "ARPA3S"
    ARRR = "ARRR"
    ARTEM = "ARTEM"
    ARV = "ARV"
    ARX = "ARX"
    ASD = "ASD"
    ASK = "ASK"
    ASM = "ASM"
    ASR = "ASR"
    ASS = "ASS"
    AST = "AST"
    ASTR = "ASTR"
    ASTR3L = "ASTR3L"
    ASTR3S = "ASTR3S"
    ASTRO = "ASTRO"
    ASW = "ASW"
    ATA = "ATA"
    ATD = "ATD"
    ATK = "ATK"
    ATLAS = "ATLAS"
    ATM = "ATM"
    ATOLO = "ATOLO"
    ATOM = "ATOM"
    ATOM3L = "ATOM3L"
    ATOM3S = "ATOM3S"
    ATP = "ATP"
    ATS = "ATS"
    AUCTION = "AUCTION"
    AUD = "AUD"
    AUDIO = "AUDIO"
    AURORA = "AURORA"
    AURY = "AURY"
    AUTO = "AUTO"
    AVA = "AVA"
    AVAX = "AVAX"
    AVAX3L = "AVAX3L"
    AVAX3S = "AVAX3S"
    AVT = "AVT"
    AXIS = "AXIS"
    AXL = "AXL"
    AXS = "AXS"
    AXS3L = "AXS3L"
    AXS3S = "AXS3S"
    AXS5L = "AXS5L"
    AXS5S = "AXS5S"
    AZERO = "AZERO"
    BABI = "BABI"
    BABY = "BABY"
    BABYDOGE = "BABYDOGE"
    BAC = "BAC"
    BACON = "BACON"
    BADGER = "BADGER"
    BAGS = "BAGS"
    BAKE = "BAKE"
    BAKED = "BAKED"
    BAL = "BAL"
    BAL3L = "BAL3L"
    BAL3S = "BAL3S"
    BAMBOO = "BAMBOO"
    BAND = "BAND"
    BANK = "BANK"
    BAO = "BAO"
    BAR = "BAR"
    BAS = "BAS"
    BASE = "BASE"
    BASIC = "BASIC"
    BAT = "BAT"
    BAT3L = "BAT3L"
    BAT3S = "BAT3S"
    BATH = "BATH"
    BAX = "BAX"
    BBANK = "BBANK"
    BBF = "BBF"
    BCD = "BCD"
    BCDN = "BCDN"
    BCH = "BCH"
    BCH3L = "BCH3L"
    BCH3S = "BCH3S"
    BCH5L = "BCH5L"
    BCH5S = "BCH5S"
    BCMC = "BCMC"
    BCN = "BCN"
    BCUG = "BCUG"
    BCX = "BCX"
    BDP = "BDP"
    BDT = "BDT"
    BEAM = "BEAM"
    BEAM3L = "BEAM3L"
    BEAM3S = "BEAM3S"
    BEEFI = "BEEFI"
    BEL = "BEL"
    BENQI = "BENQI"
    BEPRO = "BEPRO"
    BERRY = "BERRY"
    BETA = "BETA"
    BETH = "BETH"
    BETU = "BETU"
    BEYOND = "BEYOND"
    BFC = "BFC"
    BFT = "BFT"
    BHP = "BHP"
    BICO = "BICO"
    BIFI = "BIFI"
    BIFIF = "BIFIF"
    BIN = "BIN"
    BIRD = "BIRD"
    BIT = "BIT"
    BKC = "BKC"
    BLACK = "BLACK"
    BLANKV2 = "BLANKV2"
    BLES = "BLES"
    BLIN = "BLIN"
    BLOC = "BLOC"
    BLOCK = "BLOCK"
    BLOK = "BLOK"
    BLT = "BLT"
    BLY = "BLY"
    BLZ = "BLZ"
    BMI = "BMI"
    BMON = "BMON"
    BNB = "BNB"
    BNB3L = "BNB3L"
    BNB3S = "BNB3S"
    BNBDOWN = "BNBDOWN"
    BNBUP = "BNBUP"
    BNC = "BNC"
    BNS = "BNS"
    BNT = "BNT"
    BNTY = "BNTY"
    BNX = "BNX"
    BOA = "BOA"
    BOBA = "BOBA"
    BOLT = "BOLT"
    BOND = "BOND"
    BONDLY = "BONDLY"
    BONE = "BONE"
    BOO = "BOO"
    BORA = "BORA"
    BORING = "BORING"
    BOSON = "BOSON"
    BOX = "BOX"
    BP = "BP"
    BRISE = "BRISE"
    BRKL = "BRKL"
    BRT = "BRT"
    BRWL = "BRWL"
    BRY = "BRY"
    BRZ = "BRZ"
    BSCPAD = "BSCPAD"
    BSCS = "BSCS"
    BSV = "BSV"
    BSV3L = "BSV3L"
    BSV3S = "BSV3S"
    BSV5L = "BSV5L"
    BSV5S = "BSV5S"
    BSW = "BSW"
    BSW3L = "BSW3L"
    BSW3S = "BSW3S"
    BTC = "BTC"
    BTC3L = "BTC3L"
    BTC3S = "BTC3S"
    BTC5L = "BTC5L"
    BTC5S = "BTC5S"
    BTCBEAR = "BTCBEAR"
    BTCBULL = "BTCBULL"
    BTCDOM = "BTCDOM"
    BTCDOWN = "BTCDOWN"
    BTCST = "BTCST"
    BTCUP = "BTCUP"
    BTF = "BTF"
    BTG = "BTG"
    BTL = "BTL"
    BTM = "BTM"
    BTM3L = "BTM3L"
    BTM3S = "BTM3S"
    BTO = "BTO"
    BTRST = "BTRST"
    BTS = "BTS"
    BTT = "BTT"
    BTTC = "BTTC"
    BULL = "BULL"
    BURGER = "BURGER"
    BURP = "BURP"
    BUSD = "BUSD"
    BUSY = "BUSY"
    BUX = "BUX"
    BUY = "BUY"
    BXC = "BXC"
    BXH = "BXH"
    BYN = "BYN"
    BZZ = "BZZ"
    BZZ3L = "BZZ3L"
    BZZ3S = "BZZ3S"
    C98 = "C98"
    C983L = "C983L"
    C983S = "C983S"
    CAD = "CAD"
    CAKE = "CAKE"
    CAKE3L = "CAKE3L"
    CAKE3S = "CAKE3S"
    CAPS = "CAPS"
    CARD = "CARD"
    CARDS = "CARDS"
    CARR = "CARR"
    CART = "CART"
    CAS = "CAS"
    CATE = "CATE"
    CATGIRL = "CATGIRL"
    CBC = "CBC"
    CBK = "CBK"
    CCAR = "CCAR"
    CCD = "CCD"
    CEEK = "CEEK"
    CEL = "CEL"
    CELL = "CELL"
    CELO = "CELO"
    CELR = "CELR"
    CELT = "CELT"
    CERE = "CERE"
    CEUR = "CEUR"
    CFG = "CFG"
    CFI = "CFI"
    CFX = "CFX"
    CFX3L = "CFX3L"
    CFX3S = "CFX3S"
    CGG = "CGG"
    CGS = "CGS"
    CHAIN = "CHAIN"
    CHAMP = "CHAMP"
    CHAT = "CHAT"
    CHE = "CHE"
    CHEQ = "CHEQ"
    CHER = "CHER"
    CHESS = "CHESS"
    CHICKS = "CHICKS"
    CHMB = "CHMB"
    CHNG = "CHNG"
    CHR = "CHR"
    CHZ = "CHZ"
    CHZ3L = "CHZ3L"
    CHZ3S = "CHZ3S"
    CIR = "CIR"
    CIRUS = "CIRUS"
    CITY = "CITY"
    CIX100 = "CIX100"
    CKB = "CKB"
    CLH = "CLH"
    CLV = "CLV"
    CMT = "CMT"
    CNAME = "CNAME"
    CNNS = "CNNS"
    CNTM = "CNTM"
    COCOS = "COCOS"
    COFI = "COFI"
    COFIX = "COFIX"
    COMB = "COMB"
    COMBO = "COMBO"
    COMP = "COMP"
    COMP3L = "COMP3L"
    COMP3S = "COMP3S"
    CONV = "CONV"
    COOHA = "COOHA"
    COPE = "COPE"
    CORAL = "CORAL"
    CORE = "CORE"
    CORN = "CORN"
    COS = "COS"
    COTI = "COTI"
    COTI3L = "COTI3L"
    COTI3S = "COTI3S"
    COV = "COV"
    COVAL = "COVAL"
    COVER = "COVER"
    CPAN = "CPAN"
    CPOOL = "CPOOL"
    CQT = "CQT"
    CRAFT = "CRAFT"
    CRBN = "CRBN"
    CRE = "CRE"
    CRE8 = "CRE8"
    CREAM = "CREAM"
    CREDI = "CREDI"
    CREDIT = "CREDIT"
    CRF = "CRF"
    CRO = "CRO"
    CRO3L = "CRO3L"
    CRO3S = "CRO3S"
    CRP = "CRP"
    CRPT = "CRPT"
    CRT = "CRT"
    CRTS = "CRTS"
    CRU = "CRU"
    CRV = "CRV"
    CRV3L = "CRV3L"
    CRV3S = "CRV3S"
    CS = "CS"
    CSPR = "CSPR"
    CSPR3L = "CSPR3L"
    CSPR3S = "CSPR3S"
    CSTR = "CSTR"
    CTC = "CTC"
    CTI = "CTI"
    CTK = "CTK"
    CTRC = "CTRC"
    CTSI = "CTSI"
    CTT = "CTT"
    CTX = "CTX"
    CTXC = "CTXC"
    CUDOS = "CUDOS"
    CULT = "CULT"
    CUMMIES = "CUMMIES"
    CUSD = "CUSD"
    CUSDT = "CUSDT"
    CVC = "CVC"
    CVC3L = "CVC3L"
    CVC3S = "CVC3S"
    CVP = "CVP"
    CVT = "CVT"
    CVX = "CVX"
    CWAR = "CWAR"
    CWEB = "CWEB"
    CWS = "CWS"
    CYS = "CYS"
    CZZ = "CZZ"
    DAFI = "DAFI"
    DAG = "DAG"
    DAI = "DAI"
    DAL = "DAL"
    DANA = "DANA"
    DAO = "DAO"
    DAPPT = "DAPPT"
    DAPPX = "DAPPX"
    DAR = "DAR"
    DARK = "DARK"
    DASH = "DASH"
    DASH3L = "DASH3L"
    DASH3S = "DASH3S"
    DATA = "DATA"
    DAWN = "DAWN"
    DBC = "DBC"
    DCR = "DCR"
    DDD = "DDD"
    DDIM = "DDIM"
    DDOS = "DDOS"
    DEFI = "DEFI"
    DEFILAND = "DEFILAND"
    DEFIMEXT = "DEFIMEXT"
    DEGO = "DEGO"
    DEHUB = "DEHUB"
    DEK = "DEK"
    DELFI = "DELFI"
    DENT = "DENT"
    DEP = "DEP"
    DERC = "DERC"
    DERI = "DERI"
    DERO = "DERO"
    DES = "DES"
    DEUS = "DEUS"
    DEVT = "DEVT"
    DEXE = "DEXE"
    DF = "DF"
    DFA = "DFA"
    DFI = "DFI"
    DFL = "DFL"
    DFND = "DFND"
    DFY = "DFY"
    DFYN = "DFYN"
    DG = "DG"
    DGB = "DGB"
    DHT = "DHT"
    DHV = "DHV"
    DHX = "DHX"
    DIA = "DIA"
    DIGG = "DIGG"
    DILI = "DILI"
    DINO = "DINO"
    DIO = "DIO"
    DIS = "DIS"
    DIVER = "DIVER"
    DIVI = "DIVI"
    DKA = "DKA"
    DLTA = "DLTA"
    DMD = "DMD"
    DMG = "DMG"
    DMLG = "DMLG"
    DMS = "DMS"
    DMTR = "DMTR"
    DNA = "DNA"
    DNT = "DNT"
    DNXC = "DNXC"
    DOCK = "DOCK"
    DODO = "DODO"
    DOE = "DOE"
    DOG = "DOG"
    DOGA = "DOGA"
    DOGE = "DOGE"
    DOGE3L = "DOGE3L"
    DOGE3S = "DOGE3S"
    DOGE5L = "DOGE5L"
    DOGE5S = "DOGE5S"
    DOGEDASH = "DOGEDASH"
    DOGGY = "DOGGY"
    DOGNFT = "DOGNFT"
    DOME = "DOME"
    DOMI = "DOMI"
    DOP = "DOP"
    DORA = "DORA"
    DOS = "DOS"
    DOSE = "DOSE"
    DOT = "DOT"
    DOT3L = "DOT3L"
    DOT3S = "DOT3S"
    DOT5L = "DOT5L"
    DOT5S = "DOT5S"
    DOTDOWN = "DOTDOWN"
    DOTUP = "DOTUP"
    DOWS = "DOWS"
    DPET = "DPET"
    DPI = "DPI"
    DPR = "DPR"
    DPY = "DPY"
    DREAMS = "DREAMS"
    DREP = "DREP"
    DRGN = "DRGN"
    DSLA = "DSLA"
    DUCK = "DUCK"
    DUCK2 = "DUCK2"
    DUSK = "DUSK"
    DV = "DV"
    DVI = "DVI"
    DVP = "DVP"
    DVPN = "DVPN"
    DX = "DX"
    DXCT = "DXCT"
    DYDX = "DYDX"
    DYDX3L = "DYDX3L"
    DYDX3S = "DYDX3S"
    DYP = "DYP"
    EC = "EC"
    EDEN = "EDEN"
    EDG = "EDG"
    EFI = "EFI"
    EFX = "EFX"
    EGAME = "EGAME"
    EGG = "EGG"
    EGLD = "EGLD"
    EGLD3L = "EGLD3L"
    EGLD3S = "EGLD3S"
    EGS = "EGS"
    EGT = "EGT"
    EHASH = "EHASH"
    EJS = "EJS"
    ELA = "ELA"
    ELEC = "ELEC"
    ELF = "ELF"
    ELON = "ELON"
    ELT = "ELT"
    ELU = "ELU"
    EM = "EM"
    EMB = "EMB"
    EMON = "EMON"
    EMPIRE = "EMPIRE"
    ENJ = "ENJ"
    ENJ3L = "ENJ3L"
    ENJ3S = "ENJ3S"
    ENNO = "ENNO"
    ENQ = "ENQ"
    ENS = "ENS"
    ENV = "ENV"
    EOS = "EOS"
    EOS3L = "EOS3L"
    EOS3S = "EOS3S"
    EOS5L = "EOS5L"
    EOS5S = "EOS5S"
    EOSBEAR = "EOSBEAR"
    EOSBULL = "EOSBULL"
    EOSC = "EOSC"
    EOSDAC = "EOSDAC"
    EPIK = "EPIK"
    EPK = "EPK"
    EPX = "EPX"
    EQX = "EQX"
    EQZ = "EQZ"
    ERG = "ERG"
    ERN = "ERN"
    ERSDL = "ERSDL"
    ERTHA = "ERTHA"
    ESD = "ESD"
    ESG = "ESG"
    ESS = "ESS"
    ETC = "ETC"
    ETC3L = "ETC3L"
    ETC3S = "ETC3S"
    ETERNAL = "ETERNAL"
    ETH = "ETH"
    ETH2 = "ETH2"
    ETH3L = "ETH3L"
    ETH3S = "ETH3S"
    ETH5L = "ETH5L"
    ETH5S = "ETH5S"
    ETHA = "ETHA"
    ETHBEAR = "ETHBEAR"
    ETHBULL = "ETHBULL"
    ETHDOWN = "ETHDOWN"
    ETHO = "ETHO"
    ETHUP = "ETHUP"
    ETM = "ETM"
    ETN = "ETN"
    EUR = "EUR"
    EURT = "EURT"
    EVA = "EVA"
    EVER = "EVER"
    EVRY = "EVRY"
    EWT = "EWT"
    EXCH = "EXCH"
    EXE = "EXE"
    EXRD = "EXRD"
    EZ = "EZ"
    F2C = "F2C"
    FAIR = "FAIR"
    FALCONS = "FALCONS"
    FAME = "FAME"
    FAN = "FAN"
    FAR = "FAR"
    FARM = "FARM"
    FAST = "FAST"
    FCD = "FCD"
    FCL = "FCL"
    FCON = "FCON"
    FEAR = "FEAR"
    FEG = "FEG"
    FEI = "FEI"
    FET = "FET"
    FEVR = "FEVR"
    FIC = "FIC"
    FIDA = "FIDA"
    FIL = "FIL"
    FIL3L = "FIL3L"
    FIL3S = "FIL3S"
    FILDA = "FILDA"
    FIN = "FIN"
    FINE = "FINE"
    FIO = "FIO"
    FIRE = "FIRE"
    FIRO = "FIRO"
    FIS = "FIS"
    FITFI = "FITFI"
    FITFI3L = "FITFI3L"
    FITFI3S = "FITFI3S"
    FIWA = "FIWA"
    FKX = "FKX"
    FLAME = "FLAME"
    FLEX = "FLEX"
    FLM = "FLM"
    FLOKI = "FLOKI"
    FLOW = "FLOW"
    FLURRY = "FLURRY"
    FLUX = "FLUX"
    FLY = "FLY"
    FLy = "FLy"
    FODL = "FODL"
    FOR = "FOR"
    FORESTPLUS = "FORESTPLUS"
    FOREX = "FOREX"
    FORM = "FORM"
    FORTH = "FORTH"
    FOX = "FOX"
    FRA = "FRA"
    FRAX = "FRAX"
    FREE = "FREE"
    FRIN = "FRIN"
    FRM = "FRM"
    FROG = "FROG"
    FRONT = "FRONT"
    FRR = "FRR"
    FSN = "FSN"
    FST = "FST"
    FTG = "FTG"
    FTI = "FTI"
    FTM = "FTM"
    FTM3L = "FTM3L"
    FTM3S = "FTM3S"
    FTRB = "FTRB"
    FTT = "FTT"
    FTT3L = "FTT3L"
    FTT3S = "FTT3S"
    FUEL = "FUEL"
    FUN = "FUN"
    FUSE = "FUSE"
    FX = "FX"
    FXF = "FXF"
    FXS = "FXS"
    GAFI = "GAFI"
    GAIA = "GAIA"
    GAL = "GAL"
    GAL3L = "GAL3L"
    GAL3S = "GAL3S"
    GALA = "GALA"
    GALA3L = "GALA3L"
    GALA3S = "GALA3S"
    GALA5L = "GALA5L"
    GALA5S = "GALA5S"
    GALAX3L = "GALAX3L"
    GALAX3S = "GALAX3S"
    GALFAN = "GALFAN"
    GAME = "GAME"
    GAN = "GAN"
    GARD = "GARD"
    GARI = "GARI"
    GAS = "GAS"
    GASDAO = "GASDAO"
    GBP = "GBP"
    GCOIN = "GCOIN"
    GDAO = "GDAO"
    GDT = "GDT"
    GEEQ = "GEEQ"
    GEL = "GEL"
    GEM = "GEM"
    GENE = "GENE"
    GENS = "GENS"
    GF = "GF"
    GFI = "GFI"
    GGG = "GGG"
    GGM = "GGM"
    GHC = "GHC"
    GHST = "GHST"
    GHX = "GHX"
    GITCOIN = "GITCOIN"
    GLCH = "GLCH"
    GLM = "GLM"
    GLMR = "GLMR"
    GLMR3L = "GLMR3L"
    GLMR3S = "GLMR3S"
    GLQ = "GLQ"
    GM = "GM"
    GMAT = "GMAT"
    GMB = "GMB"
    GMEE = "GMEE"
    GMM = "GMM"
    GMPD = "GMPD"
    GMT = "GMT"
    GMT3L = "GMT3L"
    GMT3S = "GMT3S"
    GNO = "GNO"
    GNX = "GNX"
    GO = "GO"
    GOC = "GOC"
    GOD = "GOD"
    GODS = "GODS"
    GOF = "GOF"
    GOFX = "GOFX"
    GOG = "GOG"
    GOLD = "GOLD"
    GOLDMINER = "GOLDMINER"
    GOM2 = "GOM2"
    GOVI = "GOVI"
    GQ = "GQ"
    GRBE = "GRBE"
    GRIN = "GRIN"
    GRIN3L = "GRIN3L"
    GRIN3S = "GRIN3S"
    GRT = "GRT"
    GRT3L = "GRT3L"
    GRT3S = "GRT3S"
    GS = "GS"
    GSE = "GSE"
    GSPI = "GSPI"
    GST = "GST"
    GST3L = "GST3L"
    GST3S = "GST3S"
    GT = "GT"
    GTC = "GTC"
    GTH = "GTH"
    GTO = "GTO"
    GUM = "GUM"
    GUSD = "GUSD"
    GZONE = "GZONE"
    H2O = "H2O"
    H3RO3S = "H3RO3S"
    HAI = "HAI"
    HAKA = "HAKA"
    HAPI = "HAPI"
    HARD = "HARD"
    HAWK = "HAWK"
    HBAR = "HBAR"
    HBAR3L = "HBAR3L"
    HBAR3S = "HBAR3S"
    HBB = "HBB"
    HC = "HC"
    HCT = "HCT"
    HDAO = "HDAO"
    HDV = "HDV"
    HE = "HE"
    HEART = "HEART"
    HECH = "HECH"
    HEGIC = "HEGIC"
    HERA = "HERA"
    HERO = "HERO"
    HGET = "HGET"
    HIBIKI = "HIBIKI"
    HID = "HID"
    HIGH = "HIGH"
    HIT = "HIT"
    HIVE = "HIVE"
    HMT = "HMT"
    HNS = "HNS"
    HNT = "HNT"
    HOD = "HOD"
    HOGE = "HOGE"
    HOLY = "HOLY"
    HOPR = "HOPR"
    HORD = "HORD"
    HOT = "HOT"
    HOTCROSS = "HOTCROSS"
    HPB = "HPB"
    HSC = "HSC"
    HSF = "HSF"
    HT = "HT"
    HT3L = "HT3L"
    HT3S = "HT3S"
    HTR = "HTR"
    HUM = "HUM"
    HXRO = "HXRO"
    HYC = "HYC"
    HYDRA = "HYDRA"
    HYVE = "HYVE"
    IAG = "IAG"
    ICE = "ICE"
    ICONS = "ICONS"
    ICP = "ICP"
    ICP3L = "ICP3L"
    ICP3S = "ICP3S"
    ICX = "ICX"
    IDEA = "IDEA"
    IDEX = "IDEX"
    IDV = "IDV"
    IHT = "IHT"
    ILA = "ILA"
    ILV = "ILV"
    IMX = "IMX"
    IMX3L = "IMX3L"
    IMX3S = "IMX3S"
    INDI = "INDI"
    INJ = "INJ"
    INK = "INK"
    INSUR = "INSUR"
    INT = "INT"
    INTER = "INTER"
    INV = "INV"
    INX = "INX"
    IOEN = "IOEN"
    IOI = "IOI"
    IONX = "IONX"
    IOST = "IOST"
    IOST3L = "IOST3L"
    IOST3S = "IOST3S"
    IOTA = "IOTA"
    IOTX = "IOTX"
    IPAD = "IPAD"
    IQ = "IQ"
    IRIS = "IRIS"
    ISKY = "ISKY"
    ISP = "ISP"
    ITAMCUBE = "ITAMCUBE"
    ITC = "ITC"
    ITGR = "ITGR"
    IXS = "IXS"
    IZI = "IZI"
    JAM = "JAM"
    JAR = "JAR"
    JASMY = "JASMY"
    JASMY3L = "JASMY3L"
    JASMY3S = "JASMY3S"
    JET = "JET"
    JFI = "JFI"
    JGN = "JGN"
    JOE = "JOE"
    JST = "JST"
    JST3L = "JST3L"
    JST3S = "JST3S"
    JULD = "JULD"
    JUP = "JUP"
    JUV = "JUV"
    K21 = "K21"
    KAI = "KAI"
    KALM = "KALM"
    KAN = "KAN"
    KAR = "KAR"
    KARA = "KARA"
    KART = "KART"
    KASTA = "KASTA"
    KAT = "KAT"
    KAVA = "KAVA"
    KAVA3L = "KAVA3L"
    KAVA3S = "KAVA3S"
    KBD = "KBD"
    KBOX = "KBOX"
    KBTT = "KBTT"
    KCASH = "KCASH"
    KCS = "KCS"
    KDA = "KDA"
    KDON = "KDON"
    KEX = "KEX"
    KEY = "KEY"
    KFC = "KFC"
    KFT = "KFT"
    KGC = "KGC"
    KIBA = "KIBA"
    KIF = "KIF"
    KILT = "KILT"
    KIMCHI = "KIMCHI"
    KIN = "KIN"
    KINE = "KINE"
    KINGSHIB = "KINGSHIB"
    KINT = "KINT"
    KISHU = "KISHU"
    KLAY = "KLAY"
    KLAY3L = "KLAY3L"
    KLAY3S = "KLAY3S"
    KLO = "KLO"
    KLV = "KLV"
    KMA = "KMA"
    KMD = "KMD"
    KMON = "KMON"
    KNC = "KNC"
    KNIGHT = "KNIGHT"
    KNOT = "KNOT"
    KOK = "KOK"
    KOL = "KOL"
    KONO = "KONO"
    KP3R = "KP3R"
    KPAD = "KPAD"
    KRL = "KRL"
    KSHIB = "KSHIB"
    KSM = "KSM"
    KSM3L = "KSM3L"
    KSM3S = "KSM3S"
    KSOS = "KSOS"
    KST = "KST"
    KT = "KT"
    KTN = "KTN"
    KTON = "KTON"
    KUB = "KUB"
    KUMA = "KUMA"
    KWS = "KWS"
    KYL = "KYL"
    KZEN = "KZEN"
    L3P = "L3P"
    LABS = "LABS"
    LACE = "LACE"
    LAMB = "LAMB"
    LAND = "LAND"
    LARIX = "LARIX"
    LAT = "LAT"
    LAVA = "LAVA"
    LAVAX = "LAVAX"
    LAYER = "LAYER"
    LAZIO = "LAZIO"
    LBA = "LBA"
    LBK = "LBK"
    LBP = "LBP"
    LDN = "LDN"
    LDO = "LDO"
    LEASH = "LEASH"
    LEMD = "LEMD"
    LEMO = "LEMO"
    LEO = "LEO"
    LET = "LET"
    LEV = "LEV"
    LFW = "LFW"
    LGCY = "LGCY"
    LIEN = "LIEN"
    LIFE = "LIFE"
    LIKE = "LIKE"
    LIME = "LIME"
    LINA = "LINA"
    LINK = "LINK"
    LINK3L = "LINK3L"
    LINK3S = "LINK3S"
    LINK5L = "LINK5L"
    LINK5S = "LINK5S"
    LINKDOWN = "LINKDOWN"
    LINKUP = "LINKUP"
    LIQ = "LIQ"
    LIQUIDUS = "LIQUIDUS"
    LIT = "LIT"
    LIT3L = "LIT3L"
    LIT3S = "LIT3S"
    LITH = "LITH"
    LKR = "LKR"
    LMCH = "LMCH"
    LMR = "LMR"
    LOA = "LOA"
    LOC = "LOC"
    LOCG = "LOCG"
    LOKA = "LOKA"
    LOKA3L = "LOKA3L"
    LOKA3S = "LOKA3S"
    LON = "LON"
    LON3L = "LON3L"
    LON3S = "LON3S"
    LOOKS = "LOOKS"
    LOOKS3L = "LOOKS3L"
    LOOKS3S = "LOOKS3S"
    LOON = "LOON"
    LOOT = "LOOT"
    LOVE = "LOVE"
    LOWB = "LOWB"
    LPOOL = "LPOOL"
    LPT = "LPT"
    LRC = "LRC"
    LRC3L = "LRC3L"
    LRC3S = "LRC3S"
    LRN = "LRN"
    LSK = "LSK"
    LSS = "LSS"
    LTC = "LTC"
    LTC3L = "LTC3L"
    LTC3S = "LTC3S"
    LTC5L = "LTC5L"
    LTC5S = "LTC5S"
    LTO = "LTO"
    LTX = "LTX"
    LUA = "LUA"
    LUFFY = "LUFFY"
    LUNC = "LUNC"
    LUNR = "LUNR"
    LUS = "LUS"
    LYM = "LYM"
    LYXE = "LYXE"
    LYXe = "LYXe"
    MAGIC = "MAGIC"
    MAHA = "MAHA"
    MAKI = "MAKI"
    MAKITA = "MAKITA"
    MAN = "MAN"
    MANA = "MANA"
    MANA3L = "MANA3L"
    MANA3S = "MANA3S"
    MAP = "MAP"
    MAPE = "MAPE"
    MAPS = "MAPS"
    MARS = "MARS"
    MARS4 = "MARS4"
    MARSH = "MARSH"
    MASK = "MASK"
    MASK3L = "MASK3L"
    MASK3S = "MASK3S"
    MAT = "MAT"
    MATH = "MATH"
    MATIC = "MATIC"
    MATIC3L = "MATIC3L"
    MATIC3S = "MATIC3S"
    MATTER = "MATTER"
    MBABYDOGE = "MBABYDOGE"
    MBL = "MBL"
    MBOX = "MBOX"
    MBS = "MBS"
    MC = "MC"
    MCASH = "MCASH"
    MCB = "MCB"
    MCO = "MCO"
    MCO2 = "MCO2"
    MCRN = "MCRN"
    MDA = "MDA"
    MDF = "MDF"
    MDS = "MDS"
    MDT = "MDT"
    MDX = "MDX"
    MEAN = "MEAN"
    MED = "MED"
    MEDIA = "MEDIA"
    MELI = "MELI"
    MELON = "MELON"
    MELOS = "MELOS"
    MEM = "MEM"
    MEME = "MEME"
    MENGO = "MENGO"
    MEPAD = "MEPAD"
    MER = "MER"
    MET = "MET"
    METAG = "METAG"
    METAL = "METAL"
    METAMEXT = "METAMEXT"
    METAN = "METAN"
    METAX = "METAX"
    METIS = "METIS"
    METO = "METO"
    MFT = "MFT"
    MGA = "MGA"
    MGG = "MGG"
    MHC = "MHC"
    MHUNT = "MHUNT"
    MID = "MID"
    MILO = "MILO"
    MIMIR = "MIMIR"
    MINA = "MINA"
    MINA3L = "MINA3L"
    MINA3S = "MINA3S"
    MINI = "MINI"
    MINT = "MINT"
    MIR = "MIR"
    MIS = "MIS"
    MIST = "MIST"
    MIT = "MIT"
    MITH = "MITH"
    MITX = "MITX"
    MIX = "MIX"
    MJT = "MJT"
    MKISHU = "MKISHU"
    MKR = "MKR"
    MKR3L = "MKR3L"
    MKR3S = "MKR3S"
    MLK = "MLK"
    MLN = "MLN"
    MLS = "MLS"
    MLT = "MLT"
    MM = "MM"
    MMPRO = "MMPRO"
    MNET = "MNET"
    MNGO = "MNGO"
    MNST = "MNST"
    MNW = "MNW"
    MNY = "MNY"
    MOB = "MOB"
    MOBI = "MOBI"
    MODA = "MODA"
    MODEFI = "MODEFI"
    MOF = "MOF"
    MOFI = "MOFI"
    MOMA = "MOMA"
    MON = "MON"
    MONI = "MONI"
    MONS = "MONS"
    MOO = "MOO"
    MOOO = "MOOO"
    MOOV = "MOOV"
    MOT = "MOT"
    MOVR = "MOVR"
    MPH = "MPH"
    MQL = "MQL"
    MRCH = "MRCH"
    MSOL = "MSOL"
    MSU = "MSU"
    MSWAP = "MSWAP"
    MTA = "MTA"
    MTL = "MTL"
    MTL3L = "MTL3L"
    MTL3S = "MTL3S"
    MTN = "MTN"
    MTR = "MTR"
    MTRG = "MTRG"
    MTS = "MTS"
    MTV = "MTV"
    MULTI = "MULTI"
    MUSE = "MUSE"
    MV = "MV"
    MVDA10 = "MVDA10"
    MVDA25 = "MVDA25"
    MXC = "MXC"
    MXT = "MXT"
    MXW = "MXW"
    MYRA = "MYRA"
    NAFT = "NAFT"
    NAKA = "NAKA"
    NANO = "NANO"
    NAOS = "NAOS"
    NAP = "NAP"
    NAS = "NAS"
    NAX = "NAX"
    NBOT = "NBOT"
    NBP = "NBP"
    NBS = "NBS"
    NBT = "NBT"
    NCT = "NCT"
    NDAU = "NDAU"
    NDN = "NDN"
    NEAR = "NEAR"
    NEAR3L = "NEAR3L"
    NEAR3S = "NEAR3S"
    NEO = "NEO"
    NEO3L = "NEO3L"
    NEO3S = "NEO3S"
    NEST = "NEST"
    NEXO = "NEXO"
    NEXT = "NEXT"
    NFT = "NFT"
    NFTB = "NFTB"
    NFTD = "NFTD"
    NFTL = "NFTL"
    NFTX = "NFTX"
    NFTY = "NFTY"
    NGC = "NGC"
    NGL = "NGL"
    NGM = "NGM"
    NHCT = "NHCT"
    NIF = "NIF"
    NIFT = "NIFT"
    NIFTSY = "NIFTSY"
    NII = "NII"
    NIIFI = "NIIFI"
    NIM = "NIM"
    NKN = "NKN"
    NMR = "NMR"
    NMT = "NMT"
    NOA = "NOA"
    NOIA = "NOIA"
    NORD = "NORD"
    NOS = "NOS"
    NPT = "NPT"
    NRFB = "NRFB"
    NRV = "NRV"
    NSBT = "NSBT"
    NSDX = "NSDX"
    NSURE = "NSURE"
    NTVRK = "NTVRK"
    NULS = "NULS"
    NUM = "NUM"
    NUX = "NUX"
    NWC = "NWC"
    NYM = "NYM"
    NYZO = "NYZO"
    O3 = "O3"
    OAX = "OAX"
    OCC = "OCC"
    OCEAN = "OCEAN"
    OCN = "OCN"
    OCT = "OCT"
    OCTO = "OCTO"
    ODDZ = "ODDZ"
    OG = "OG"
    OGN = "OGN"
    OHM = "OHM"
    OIN = "OIN"
    OKB = "OKB"
    OKB3L = "OKB3L"
    OKB3S = "OKB3S"
    OKT = "OKT"
    OLT = "OLT"
    OLV = "OLV"
    OLY = "OLY"
    OM = "OM"
    OMG = "OMG"
    OMG3L = "OMG3L"
    OMG3S = "OMG3S"
    OMI = "OMI"
    ONC = "ONC"
    ONE = "ONE"
    ONE3L = "ONE3L"
    ONE3S = "ONE3S"
    ONG = "ONG"
    ONIT = "ONIT"
    ONS = "ONS"
    ONSTON = "ONSTON"
    ONT = "ONT"
    ONT3L = "ONT3L"
    ONT3S = "ONT3S"
    ONX = "ONX"
    OOE = "OOE"
    OOKI = "OOKI"
    OPA = "OPA"
    OPCT = "OPCT"
    OPEN = "OPEN"
    OPIUM = "OPIUM"
    OPS = "OPS"
    OPUL = "OPUL"
    ORAI = "ORAI"
    ORAO = "ORAO"
    ORB = "ORB"
    ORBR = "ORBR"
    ORBS = "ORBS"
    ORC = "ORC"
    ORCA = "ORCA"
    ORION = "ORION"
    ORN = "ORN"
    ORO = "ORO"
    ORS = "ORS"
    ORT = "ORT"
    OST = "OST"
    OUSD = "OUSD"
    OVR = "OVR"
    OXEN = "OXEN"
    OXT = "OXT"
    OXY = "OXY"
    PAF = "PAF"
    PARA = "PARA"
    PAXG = "PAXG"
    PAY = "PAY"
    PBR = "PBR"
    PBTC35A = "PBTC35A"
    PBX = "PBX"
    PCI = "PCI"
    PCNT = "PCNT"
    PCX = "PCX"
    PDEX = "PDEX"
    PEARL = "PEARL"
    PEL = "PEL"
    PENDLE = "PENDLE"
    PEOPLE = "PEOPLE"
    PEOPLE3L = "PEOPLE3L"
    PEOPLE3S = "PEOPLE3S"
    PERA = "PERA"
    PERC = "PERC"
    PERI = "PERI"
    PERL = "PERL"
    PERP = "PERP"
    PET = "PET"
    PHA = "PHA"
    PHM = "PHM"
    PHNX = "PHNX"
    PHTR = "PHTR"
    PI = "PI"
    PICKLE = "PICKLE"
    PIG = "PIG"
    PING = "PING"
    PIT = "PIT"
    PIVX = "PIVX"
    PIXEL = "PIXEL"
    PIZA = "PIZA"
    PKF = "PKF"
    PLA = "PLA"
    PLACE = "PLACE"
    PLATO = "PLATO"
    PLD = "PLD"
    PLG = "PLG"
    PLGR = "PLGR"
    PLSPAD = "PLSPAD"
    PLU = "PLU"
    PLY = "PLY"
    PMON = "PMON"
    PNG = "PNG"
    PNK = "PNK"
    PNL = "PNL"
    PNT = "PNT"
    POG = "POG"
    POKT = "POKT"
    POL = "POL"
    POLC = "POLC"
    POLI = "POLI"
    POLIS = "POLIS"
    POLK = "POLK"
    POLS = "POLS"
    POLX = "POLX"
    POLY = "POLY"
    POLYDOGE = "POLYDOGE"
    POLYPAD = "POLYPAD"
    POND = "POND"
    POOL = "POOL"
    POOLZ = "POOLZ"
    PORT = "PORT"
    PORTO = "PORTO"
    POSI = "POSI"
    POT = "POT"
    POWR = "POWR"
    PPAD = "PPAD"
    PPT = "PPT"
    PRARE = "PRARE"
    PRE = "PRE"
    PRIDE = "PRIDE"
    PRISM = "PRISM"
    PRIV = "PRIV"
    PROM = "PROM"
    PROPS = "PROPS"
    PROS = "PROS"
    PRQ = "PRQ"
    PRT = "PRT"
    PSB = "PSB"
    PSG = "PSG"
    PSL = "PSL"
    PSP = "PSP"
    PST = "PST"
    PSTAKE = "PSTAKE"
    PSY = "PSY"
    PTU = "PTU"
    PUNDIX = "PUNDIX"
    PUSH = "PUSH"
    PVU = "PVU"
    PWAR = "PWAR"
    PYM = "PYM"
    PYR = "PYR"
    QANX = "QANX"
    QASH = "QASH"
    QBT = "QBT"
    QI = "QI"
    QKC = "QKC"
    QLC = "QLC"
    QNT = "QNT"
    QOM = "QOM"
    QRDO = "QRDO"
    QSP = "QSP"
    QTC = "QTC"
    QTCON = "QTCON"
    QTUM = "QTUM"
    QTUM3L = "QTUM3L"
    QTUM3S = "QTUM3S"
    QUACK = "QUACK"
    QUICK = "QUICK"
    RACA = "RACA"
    RACA3L = "RACA3L"
    RACA3S = "RACA3S"
    RACEFI = "RACEFI"
    RAD = "RAD"
    RAGE = "RAGE"
    RAI = "RAI"
    RAM = "RAM"
    RAMP = "RAMP"
    RANKER = "RANKER"
    RARE = "RARE"
    RARI = "RARI"
    RATING = "RATING"
    RATIO = "RATIO"
    RAY = "RAY"
    RAY3L = "RAY3L"
    RAY3S = "RAY3S"
    RAZE = "RAZE"
    RAZOR = "RAZOR"
    RBC = "RBC"
    RBLS = "RBLS"
    RBN = "RBN"
    RCN = "RCN"
    RDN = "RDN"
    REAL = "REAL"
    REALM = "REALM"
    REAP = "REAP"
    RED = "RED"
    REEF = "REEF"
    REF = "REF"
    REI = "REI"
    REM = "REM"
    REN = "REN"
    RENA = "RENA"
    RENBTC = "RENBTC"
    REP = "REP"
    REQ = "REQ"
    REV = "REV"
    REVO = "REVO"
    REVU = "REVU"
    REVV = "REVV"
    RFOX = "RFOX"
    RFR = "RFR"
    RFUEL = "RFUEL"
    RICE = "RICE"
    RIDE = "RIDE"
    RIF = "RIF"
    RIM = "RIM"
    RIN = "RIN"
    RING = "RING"
    RIO = "RIO"
    RITE = "RITE"
    RLC = "RLC"
    RLY = "RLY"
    RMRK = "RMRK"
    RNDR = "RNDR"
    RNT = "RNT"
    ROAD = "ROAD"
    ROAR = "ROAR"
    ROCO = "ROCO"
    RON = "RON"
    ROOBEE = "ROOBEE"
    ROOK = "ROOK"
    ROOM = "ROOM"
    ROSE = "ROSE"
    ROSE3L = "ROSE3L"
    ROSE3S = "ROSE3S"
    ROSN = "ROSN"
    ROUTE = "ROUTE"
    RPC = "RPC"
    RSR = "RSR"
    RSS3 = "RSS3"
    RSV = "RSV"
    RUFF = "RUFF"
    RUNE = "RUNE"
    RUNE3L = "RUNE3L"
    RUNE3S = "RUNE3S"
    RVC = "RVC"
    RVN = "RVN"
    SAFEMARS = "SAFEMARS"
    SAITAMA = "SAITAMA"
    SAITO = "SAITO"
    SAKE = "SAKE"
    SALT = "SALT"
    SAMO = "SAMO"
    SAND = "SAND"
    SAND3L = "SAND3L"
    SAND3S = "SAND3S"
    SANDWICH = "SANDWICH"
    SANTOS = "SANTOS"
    SAO = "SAO"
    SASHIMI = "SASHIMI"
    SAVG = "SAVG"
    SB = "SB"
    SBR = "SBR"
    SBTC = "SBTC"
    SC = "SC"
    SCLP = "SCLP"
    SCNSOL = "SCNSOL"
    SCRT = "SCRT"
    SCY = "SCY"
    SD = "SD"
    SDAO = "SDAO"
    SDN = "SDN"
    SECO = "SECO"
    SENATE = "SENATE"
    SENC = "SENC"
    SENSO = "SENSO"
    SERO = "SERO"
    SERO3L = "SERO3L"
    SERO3S = "SERO3S"
    SFG = "SFG"
    SFI = "SFI"
    SFIL = "SFIL"
    SFM = "SFM"
    SFP = "SFP"
    SFUND = "SFUND"
    SGB = "SGB"
    SHA = "SHA"
    SHARE = "SHARE"
    SHFT = "SHFT"
    SHI = "SHI"
    SHIB = "SHIB"
    SHIB1000 = "SHIB1000"
    SHIB3L = "SHIB3L"
    SHIB3S = "SHIB3S"
    SHIB5L = "SHIB5L"
    SHIB5S = "SHIB5S"
    SHILL = "SHILL"
    SHIT = "SHIT"
    SHOE = "SHOE"
    SHOPX = "SHOPX"
    SHR = "SHR"
    SHX = "SHX"
    SIDUS = "SIDUS"
    SIN = "SIN"
    SINGLE = "SINGLE"
    SIS = "SIS"
    SKEY = "SKEY"
    SKILL = "SKILL"
    SKL = "SKL"
    SKL3L = "SKL3L"
    SKL3S = "SKL3S"
    SKM = "SKM"
    SKRT = "SKRT"
    SKT = "SKT"
    SKU = "SKU"
    SKYRIM = "SKYRIM"
    SLC = "SLC"
    SLCL = "SLCL"
    SLICE = "SLICE"
    SLIM = "SLIM"
    SLM = "SLM"
    SLND = "SLND"
    SLNV2 = "SLNV2"
    SLP = "SLP"
    SLP3L = "SLP3L"
    SLP3S = "SLP3S"
    SLRS = "SLRS"
    SMG = "SMG"
    SMT = "SMT"
    SMTY = "SMTY"
    SNET = "SNET"
    SNFT = "SNFT"
    SNK = "SNK"
    SNOW = "SNOW"
    SNT = "SNT"
    SNTR = "SNTR"
    SNX = "SNX"
    SNX3L = "SNX3L"
    SNX3S = "SNX3S"
    SNY = "SNY"
    SOC = "SOC"
    SOL = "SOL"
    SOL3L = "SOL3L"
    SOL3S = "SOL3S"
    SOLO = "SOLO"
    SOLR = "SOLR"
    SOLVE = "SOLVE"
    SON = "SON"
    SONAR = "SONAR"
    SOP = "SOP"
    SOS = "SOS"
    SOUL = "SOUL"
    SOURCE = "SOURCE"
    SOV = "SOV"
    SPA = "SPA"
    SPAY = "SPAY"
    SPELL = "SPELL"
    SPELLFIRE = "SPELLFIRE"
    SPHRI = "SPHRI"
    SPI = "SPI"
    SPIRIT = "SPIRIT"
    SPO = "SPO"
    SPS = "SPS"
    SQUID = "SQUID"
    SRK = "SRK"
    SRM = "SRM"
    SRM3L = "SRM3L"
    SRM3S = "SRM3S"
    SRN = "SRN"
    SRP = "SRP"
    SSV = "SSV"
    SSX = "SSX"
    STAR = "STAR"
    STARL = "STARL"
    STARLY = "STARLY"
    STARS = "STARS"
    STBU = "STBU"
    STC = "STC"
    STEEM = "STEEM"
    STEP = "STEP"
    STEPG = "STEPG"
    STETH = "STETH"
    STG = "STG"
    STI = "STI"
    STMX = "STMX"
    STN = "STN"
    STND = "STND"
    STORE = "STORE"
    STORJ = "STORJ"
    STOS = "STOS"
    STOX = "STOX"
    STPT = "STPT"
    STR = "STR"
    STRAX = "STRAX"
    STRK = "STRK"
    STRM = "STRM"
    STRONG = "STRONG"
    STRP = "STRP"
    STSOL = "STSOL"
    STX = "STX"
    STZ = "STZ"
    SUKU = "SUKU"
    SUN = "SUN"
    SUNNY = "SUNNY"
    SUP = "SUP"
    SUPE = "SUPE"
    SUPER = "SUPER"
    SURV = "SURV"
    SUSD = "SUSD"
    SUSHI = "SUSHI"
    SUSHI3L = "SUSHI3L"
    SUSHI3S = "SUSHI3S"
    SUTER = "SUTER"
    SVT = "SVT"
    SWAP = "SWAP"
    SWASH = "SWASH"
    SWAY = "SWAY"
    SWFTC = "SWFTC"
    SWINGBY = "SWINGBY"
    SWOP = "SWOP"
    SWP = "SWP"
    SWRV = "SWRV"
    SWTH = "SWTH"
    SXP = "SXP"
    SXP3L = "SXP3L"
    SXP3S = "SXP3S"
    SYLO = "SYLO"
    SYN = "SYN"
    SYNR = "SYNR"
    SYS = "SYS"
    T = "T"
    TABOO = "TABOO"
    TAI = "TAI"
    TAKI = "TAKI"
    TALK = "TALK"
    TAP = "TAP"
    TARA = "TARA"
    TAUM = "TAUM"
    TAUR = "TAUR"
    TBE = "TBE"
    TCP = "TCP"
    TCT = "TCT"
    TDROP = "TDROP"
    TEER = "TEER"
    TEL = "TEL"
    TFUEL = "TFUEL"
    THEOS = "THEOS"
    THETA = "THETA"
    THETA3L = "THETA3L"
    THETA3S = "THETA3S"
    THG = "THG"
    THN = "THN"
    TIDAL = "TIDAL"
    TIME = "TIME"
    TIMECHRONO = "TIMECHRONO"
    TIP = "TIP"
    TIPS = "TIPS"
    TITA = "TITA"
    TITAN = "TITAN"
    TKO = "TKO"
    TLM = "TLM"
    TLOS = "TLOS"
    TMTG = "TMTG"
    TNC = "TNC"
    TOKAU = "TOKAU"
    TOKE = "TOKE"
    TOKO = "TOKO"
    TOMO = "TOMO"
    TON = "TON"
    TONCOIN = "TONCOIN"
    TONE = "TONE"
    TOOLS = "TOOLS"
    TOPC = "TOPC"
    TORN = "TORN"
    TOTM = "TOTM"
    TOWER = "TOWER"
    TOWN = "TOWN"
    TPT = "TPT"
    TRA = "TRA"
    TRACE = "TRACE"
    TRADE = "TRADE"
    TRB = "TRB"
    TRIAS = "TRIAS"
    TRIBE = "TRIBE"
    TRIBE3L = "TRIBE3L"
    TRIBE3S = "TRIBE3S"
    TRIO = "TRIO"
    TROY = "TROY"
    TRU = "TRU"
    TRUE = "TRUE"
    TRVL = "TRVL"
    TRX = "TRX"
    TRX3L = "TRX3L"
    TRX3S = "TRX3S"
    TRXDOWN = "TRXDOWN"
    TRXUP = "TRXUP"
    TRYB = "TRYB"
    TSHP = "TSHP"
    TSL = "TSL"
    TT = "TT"
    TTK = "TTK"
    TTT = "TTT"
    TULIP = "TULIP"
    TUP = "TUP"
    TUSD = "TUSD"
    TVK = "TVK"
    TWT = "TWT"
    TXA = "TXA"
    TXT = "TXT"
    UBTC = "UBTC"
    UBX = "UBX"
    UBXS = "UBXS"
    UBXT = "UBXT"
    UDO = "UDO"
    UFI = "UFI"
    UFO = "UFO"
    UFT = "UFT"
    ULU = "ULU"
    UMA = "UMA"
    UMB = "UMB"
    UMEE = "UMEE"
    UMX = "UMX"
    UNB = "UNB"
    UNCX = "UNCX"
    UNDEAD = "UNDEAD"
    UNFI = "UNFI"
    UNI = "UNI"
    UNI3L = "UNI3L"
    UNI3S = "UNI3S"
    UNI5L = "UNI5L"
    UNI5S = "UNI5S"
    UNIC = "UNIC"
    UNISTAKE = "UNISTAKE"
    UNISWAP = "UNISWAP"
    UNN = "UNN"
    UNO = "UNO"
    UNQ = "UNQ"
    UOS = "UOS"
    UPI = "UPI"
    UPO = "UPO"
    URUS = "URUS"
    USDC = "USDC"
    USDD = "USDD"
    USDG = "USDG"
    USDJ = "USDJ"
    USDN = "USDN"
    USDP = "USDP"
    USDT = "USDT"
    USTC = "USTC"
    UTK = "UTK"
    VADER = "VADER"
    VAI = "VAI"
    VALUE = "VALUE"
    VDR = "VDR"
    VEE = "VEE"
    VEED = "VEED"
    VEGA = "VEGA"
    VELO = "VELO"
    VEMP = "VEMP"
    VENT = "VENT"
    VERA = "VERA"
    VET = "VET"
    VET3L = "VET3L"
    VET3S = "VET3S"
    VGX = "VGX"
    VID = "VID"
    VIDT = "VIDT"
    VIDY = "VIDY"
    VIDYX = "VIDYX"
    VISION = "VISION"
    VITE = "VITE"
    VLX = "VLX"
    VLXPAD = "VLXPAD"
    VOXEL = "VOXEL"
    VR = "VR"
    VRA = "VRA"
    VRT = "VRT"
    VRX = "VRX"
    VSO = "VSO"
    VSP = "VSP"
    VSYS = "VSYS"
    VTG = "VTG"
    VTHO = "VTHO"
    VXV = "VXV"
    WAG = "WAG"
    WAGYU = "WAGYU"
    WAL = "WAL"
    WALLET = "WALLET"
    WAM = "WAM"
    WAN = "WAN"
    WAR = "WAR"
    WAVES = "WAVES"
    WAVES3L = "WAVES3L"
    WAVES3S = "WAVES3S"
    WAXP = "WAXP"
    WBTC = "WBTC"
    WEAR = "WEAR"
    WEMIX = "WEMIX"
    WEST = "WEST"
    WEX = "WEX"
    WFLOW = "WFLOW"
    WGRT = "WGRT"
    WHALE = "WHALE"
    WHITE = "WHITE"
    WICC = "WICC"
    WIKEN = "WIKEN"
    WILD = "WILD"
    WIN = "WIN"
    WING = "WING"
    WIT = "WIT"
    WMT = "WMT"
    WNCG = "WNCG"
    WNDR = "WNDR"
    WNXM = "WNXM"
    WNZ = "WNZ"
    WOM = "WOM"
    WOO = "WOO"
    WOO3L = "WOO3L"
    WOO3S = "WOO3S"
    WOOP = "WOOP"
    WOZX = "WOZX"
    WRX = "WRX"
    WSB = "WSB"
    WSG = "WSG"
    WSIENNA = "WSIENNA"
    WTC = "WTC"
    WWY = "WWY"
    WXT = "WXT"
    WZRD = "WZRD"
    XAUG = "XAUG"
    XAUT = "XAUT"
    XAVA = "XAVA"
    XBT = "XBT"
    XCAD = "XCAD"
    XCH = "XCH"
    XCH3L = "XCH3L"
    XCH3S = "XCH3S"
    XCN = "XCN"
    XCUR = "XCUR"
    XCV = "XCV"
    XDB = "XDB"
    XDC = "XDC"
    XDEFI = "XDEFI"
    XEC = "XEC"
    XEC3L = "XEC3L"
    XEC3S = "XEC3S"
    XED = "XED"
    XEM = "XEM"
    XEND = "XEND"
    XHV = "XHV"
    XIL = "XIL"
    XLM = "XLM"
    XLM3L = "XLM3L"
    XLM3S = "XLM3S"
    XMARK = "XMARK"
    XMC = "XMC"
    XMR = "XMR"
    XMR3L = "XMR3L"
    XMR3S = "XMR3S"
    XNFT = "XNFT"
    XNL = "XNL"
    XNO = "XNO"
    XOR = "XOR"
    XPNET = "XPNET"
    XPO = "XPO"
    XPR = "XPR"
    XPRESS = "XPRESS"
    XPRT = "XPRT"
    XRP = "XRP"
    XRP3L = "XRP3L"
    XRP3S = "XRP3S"
    XRP5L = "XRP5L"
    XRP5S = "XRP5S"
    XRPBEAR = "XRPBEAR"
    XRPBULL = "XRPBULL"
    XRPDOWN = "XRPDOWN"
    XRPUP = "XRPUP"
    XRUNE = "XRUNE"
    XSR = "XSR"
    XTAG = "XTAG"
    XTM = "XTM"
    XTZ = "XTZ"
    XTZ3L = "XTZ3L"
    XTZ3S = "XTZ3S"
    XUC = "XUC"
    XVG = "XVG"
    XVS = "XVS"
    XWG = "XWG"
    XY = "XY"
    XYM = "XYM"
    XYO = "XYO"
    YAM = "YAM"
    YCT = "YCT"
    YEE = "YEE"
    YFDAI = "YFDAI"
    YFI = "YFI"
    YFI3L = "YFI3L"
    YFI3S = "YFI3S"
    YFII = "YFII"
    YFII3L = "YFII3L"
    YFII3S = "YFII3S"
    YFX = "YFX"
    YGG = "YGG"
    YIELD = "YIELD"
    YIN = "YIN"
    YLD = "YLD"
    YOOSHI = "YOOSHI"
    YOP = "YOP"
    YOU = "YOU"
    YOYO = "YOYO"
    ZAM = "ZAM"
    ZBC = "ZBC"
    ZCN = "ZCN"
    ZCX = "ZCX"
    ZEC = "ZEC"
    ZEC3L = "ZEC3L"
    ZEC3S = "ZEC3S"
    ZEE = "ZEE"
    ZEN = "ZEN"
    ZEN3L = "ZEN3L"
    ZEN3S = "ZEN3S"
    ZEUM = "ZEUM"
    ZIG = "ZIG"
    ZIL = "ZIL"
    ZIL3L = "ZIL3L"
    ZIL3S = "ZIL3S"
    ZINU = "ZINU"
    ZKS = "ZKS"
    ZKT = "ZKT"
    ZLK = "ZLK"
    ZLW = "ZLW"
    ZMT = "ZMT"
    ZODI = "ZODI"
    ZONE = "ZONE"
    ZOON = "ZOON"
    ZPT = "ZPT"
    ZRX = "ZRX"
    ZSC = "ZSC"
    ZYRO = "ZYRO"
    aUSD = "aUSD"
    cUSD = "cUSD"
    flexUSD = "flexUSD"
