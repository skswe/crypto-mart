from ...enums import InstrumentType, Symbol

instrument_names = {
    InstrumentType.SPOT: {
        Symbol._10000NFT: "10000NFTUSDT",
        Symbol._1000BTT: "1000BTTUSDT",
        Symbol._1000XEC: "1000XECUSDT",
        Symbol._1INCH: "1INCHUSDT",
        Symbol.AAVE: "AAVEUSDT",
        Symbol.ACH: "ACHUSDT",
        Symbol.ADA: "ADAUSDT",
        Symbol.AGLD: "AGLDUSDT",
        Symbol.AKRO: "AKROUSDT",
        Symbol.ALGO: "ALGOUSDT",
        Symbol.ALICE: "ALICEUSDT",
        Symbol.ALPHA: "ALPHAUSDT",
        Symbol.ANKR: "ANKRUSDT",
        Symbol.ANT: "ANTUSDT",
        Symbol.APE: "APEUSDT",
        Symbol.API3: "API3USDT",
        Symbol.AR: "ARUSDT",
        Symbol.ARPA: "ARPAUSDT",
        Symbol.ASTR: "ASTRUSDT",
        Symbol.ATOM: "ATOMUSDT",
        Symbol.AUDIO: "AUDIOUSDT",
        Symbol.AVAX: "AVAXUSDT",
        Symbol.AXS: "AXSUSDT",
        Symbol.BAKE: "BAKEUSDT",
        Symbol.BAL: "BALUSDT",
        Symbol.BAND: "BANDUSDT",
        Symbol.BAT: "BATUSDT",
        Symbol.BCH: "BCHUSDT",
        Symbol.BICO: "BICOUSDT",
        Symbol.BIT: "BITUSDT",
        Symbol.BNB: "BNBUSDT",
        Symbol.BNX: "BNXUSDT",
        Symbol.BOBA: "BOBAUSDT",
        Symbol.BSV: "BSVUSDT",
        Symbol.BSW: "BSWUSDT",
        Symbol.BTC: "BTCUSDT",
        Symbol.C98: "C98USDT",
        Symbol.CELO: "CELOUSDT",
        Symbol.CELR: "CELRUSDT",
        Symbol.CHR: "CHRUSDT",
        Symbol.CHZ: "CHZUSDT",
        Symbol.CKB: "CKBUSDT",
        Symbol.COMP: "COMPUSDT",
        Symbol.COTI: "COTIUSDT",
        Symbol.CREAM: "CREAMUSDT",
        Symbol.CRO: "CROUSDT",
        Symbol.CRV: "CRVUSDT",
        Symbol.CTC: "CTCUSDT",
        Symbol.CTK: "CTKUSDT",
        Symbol.CTSI: "CTSIUSDT",
        Symbol.CVC: "CVCUSDT",
        Symbol.CVX: "CVXUSDT",
        Symbol.DAR: "DARUSDT",
        Symbol.DASH: "DASHUSDT",
        Symbol.DENT: "DENTUSDT",
        Symbol.DGB: "DGBUSDT",
        Symbol.DODO: "DODOUSDT",
        Symbol.DOGE: "DOGEUSDT",
        Symbol.DOT: "DOTUSDT",
        Symbol.DUSK: "DUSKUSDT",
        Symbol.DYDX: "DYDXUSDT",
        Symbol.EGLD: "EGLDUSDT",
        Symbol.ENJ: "ENJUSDT",
        Symbol.ENS: "ENSUSDT",
        Symbol.EOS: "EOSUSDT",
        Symbol.ETC: "ETCUSDT",
        Symbol.ETH: "ETHUSDT",
        Symbol.FIL: "FILUSDT",
        Symbol.FITFI: "FITFIUSDT",
        Symbol.FLM: "FLMUSDT",
        Symbol.FLOW: "FLOWUSDT",
        Symbol.FTM: "FTMUSDT",
        Symbol.FTT: "FTTUSDT",
        Symbol.FXS: "FXSUSDT",
        Symbol.GAL: "GALUSDT",
        Symbol.GALA: "GALAUSDT",
        Symbol.GLMR: "GLMRUSDT",
        Symbol.GMT: "GMTUSDT",
        Symbol.GRT: "GRTUSDT",
        Symbol.GST: "GSTUSDT",
        Symbol.GTC: "GTCUSDT",
        Symbol.HBAR: "HBARUSDT",
        Symbol.HNT: "HNTUSDT",
        Symbol.HOT: "HOTUSDT",
        Symbol.ICP: "ICPUSDT",
        Symbol.ICX: "ICXUSDT",
        Symbol.ILV: "ILVUSDT",
        Symbol.IMX: "IMXUSDT",
        Symbol.IOST: "IOSTUSDT",
        Symbol.IOTA: "IOTAUSDT",
        Symbol.IOTX: "IOTXUSDT",
        Symbol.JASMY: "JASMYUSDT",
        Symbol.JST: "JSTUSDT",
        Symbol.KAVA: "KAVAUSDT",
        Symbol.KDA: "KDAUSDT",
        Symbol.KLAY: "KLAYUSDT",
        Symbol.KNC: "KNCUSDT",
        Symbol.KSM: "KSMUSDT",
        Symbol.LINA: "LINAUSDT",
        Symbol.LINK: "LINKUSDT",
        Symbol.LIT: "LITUSDT",
        Symbol.LOOKS: "LOOKSUSDT",
        Symbol.LPT: "LPTUSDT",
        Symbol.LRC: "LRCUSDT",
        Symbol.LTC: "LTCUSDT",
        Symbol.MANA: "MANAUSDT",
        Symbol.MASK: "MASKUSDT",
        Symbol.MATIC: "MATICUSDT",
        Symbol.MINA: "MINAUSDT",
        Symbol.MKR: "MKRUSDT",
        Symbol.MTL: "MTLUSDT",
        Symbol.NEAR: "NEARUSDT",
        Symbol.NEO: "NEOUSDT",
        Symbol.OCEAN: "OCEANUSDT",
        Symbol.OGN: "OGNUSDT",
        Symbol.OMG: "OMGUSDT",
        Symbol.ONE: "ONEUSDT",
        Symbol.PAXG: "PAXGUSDT",
        Symbol.PEOPLE: "PEOPLEUSDT",
        Symbol.QTUM: "QTUMUSDT",
        Symbol.RAY: "RAYUSDT",
        Symbol.REEF: "REEFUSDT",
        Symbol.REN: "RENUSDT",
        Symbol.REQ: "REQUSDT",
        Symbol.RNDR: "RNDRUSDT",
        Symbol.ROSE: "ROSEUSDT",
        Symbol.RSR: "RSRUSDT",
        Symbol.RSS3: "RSS3USDT",
        Symbol.RUNE: "RUNEUSDT",
        Symbol.RVN: "RVNUSDT",
        Symbol.SAND: "SANDUSDT",
        Symbol.SC: "SCUSDT",
        Symbol.SCRT: "SCRTUSDT",
        Symbol.SFP: "SFPUSDT",
        Symbol.SHIB1000: "SHIB1000USDT",
        Symbol.SKL: "SKLUSDT",
        Symbol.SLP: "SLPUSDT",
        Symbol.SNX: "SNXUSDT",
        Symbol.SOL: "SOLUSDT",
        Symbol.SPELL: "SPELLUSDT",
        Symbol.SRM: "SRMUSDT",
        Symbol.STMX: "STMXUSDT",
        Symbol.STORJ: "STORJUSDT",
        Symbol.STX: "STXUSDT",
        Symbol.SUN: "SUNUSDT",
        Symbol.SUSHI: "SUSHIUSDT",
        Symbol.SXP: "SXPUSDT",
        Symbol.THETA: "THETAUSDT",
        Symbol.TLM: "TLMUSDT",
        Symbol.TOMO: "TOMOUSDT",
        Symbol.TRX: "TRXUSDT",
        Symbol.UNI: "UNIUSDT",
        Symbol.VET: "VETUSDT",
        Symbol.WAVES: "WAVESUSDT",
        Symbol.WOO: "WOOUSDT",
        Symbol.XCN: "XCNUSDT",
        Symbol.XEM: "XEMUSDT",
        Symbol.XLM: "XLMUSDT",
        Symbol.XMR: "XMRUSDT",
        Symbol.XRP: "XRPUSDT",
        Symbol.XTZ: "XTZUSDT",
        Symbol.YFI: "YFIUSDT",
        Symbol.YGG: "YGGUSDT",
        Symbol.ZEC: "ZECUSDT",
        Symbol.ZEN: "ZENUSDT",
        Symbol.ZIL: "ZILUSDT",
        Symbol.ZRX: "ZRXUSDT",
    },
    InstrumentType.SPOT: {
        Symbol._10000NFT: "10000NFTUSDT",
        Symbol._1000BTT: "1000BTTUSDT",
        Symbol._1000XEC: "1000XECUSDT",
        Symbol._1INCH: "1INCHUSDT",
        Symbol.AAVE: "AAVEUSDT",
        Symbol.ACH: "ACHUSDT",
        Symbol.ADA: "ADAUSDT",
        Symbol.AGLD: "AGLDUSDT",
        Symbol.AKRO: "AKROUSDT",
        Symbol.ALGO: "ALGOUSDT",
        Symbol.ALICE: "ALICEUSDT",
        Symbol.ALPHA: "ALPHAUSDT",
        Symbol.ANKR: "ANKRUSDT",
        Symbol.ANT: "ANTUSDT",
        Symbol.APE: "APEUSDT",
        Symbol.API3: "API3USDT",
        Symbol.AR: "ARUSDT",
        Symbol.ARPA: "ARPAUSDT",
        Symbol.ASTR: "ASTRUSDT",
        Symbol.ATOM: "ATOMUSDT",
        Symbol.AUDIO: "AUDIOUSDT",
        Symbol.AVAX: "AVAXUSDT",
        Symbol.AXS: "AXSUSDT",
        Symbol.BAKE: "BAKEUSDT",
        Symbol.BAL: "BALUSDT",
        Symbol.BAND: "BANDUSDT",
        Symbol.BAT: "BATUSDT",
        Symbol.BCH: "BCHUSDT",
        Symbol.BICO: "BICOUSDT",
        Symbol.BIT: "BITUSDT",
        Symbol.BNB: "BNBUSDT",
        Symbol.BNX: "BNXUSDT",
        Symbol.BOBA: "BOBAUSDT",
        Symbol.BSV: "BSVUSDT",
        Symbol.BSW: "BSWUSDT",
        Symbol.BTC: "BTCUSDT",
        Symbol.C98: "C98USDT",
        Symbol.CELO: "CELOUSDT",
        Symbol.CELR: "CELRUSDT",
        Symbol.CHR: "CHRUSDT",
        Symbol.CHZ: "CHZUSDT",
        Symbol.CKB: "CKBUSDT",
        Symbol.COMP: "COMPUSDT",
        Symbol.COTI: "COTIUSDT",
        Symbol.CREAM: "CREAMUSDT",
        Symbol.CRO: "CROUSDT",
        Symbol.CRV: "CRVUSDT",
        Symbol.CTC: "CTCUSDT",
        Symbol.CTK: "CTKUSDT",
        Symbol.CTSI: "CTSIUSDT",
        Symbol.CVC: "CVCUSDT",
        Symbol.CVX: "CVXUSDT",
        Symbol.DAR: "DARUSDT",
        Symbol.DASH: "DASHUSDT",
        Symbol.DENT: "DENTUSDT",
        Symbol.DGB: "DGBUSDT",
        Symbol.DODO: "DODOUSDT",
        Symbol.DOGE: "DOGEUSDT",
        Symbol.DOT: "DOTUSDT",
        Symbol.DUSK: "DUSKUSDT",
        Symbol.DYDX: "DYDXUSDT",
        Symbol.EGLD: "EGLDUSDT",
        Symbol.ENJ: "ENJUSDT",
        Symbol.ENS: "ENSUSDT",
        Symbol.EOS: "EOSUSDT",
        Symbol.ETC: "ETCUSDT",
        Symbol.ETH: "ETHUSDT",
        Symbol.FIL: "FILUSDT",
        Symbol.FITFI: "FITFIUSDT",
        Symbol.FLM: "FLMUSDT",
        Symbol.FLOW: "FLOWUSDT",
        Symbol.FTM: "FTMUSDT",
        Symbol.FTT: "FTTUSDT",
        Symbol.FXS: "FXSUSDT",
        Symbol.GAL: "GALUSDT",
        Symbol.GALA: "GALAUSDT",
        Symbol.GLMR: "GLMRUSDT",
        Symbol.GMT: "GMTUSDT",
        Symbol.GRT: "GRTUSDT",
        Symbol.GST: "GSTUSDT",
        Symbol.GTC: "GTCUSDT",
        Symbol.HBAR: "HBARUSDT",
        Symbol.HNT: "HNTUSDT",
        Symbol.HOT: "HOTUSDT",
        Symbol.ICP: "ICPUSDT",
        Symbol.ICX: "ICXUSDT",
        Symbol.ILV: "ILVUSDT",
        Symbol.IMX: "IMXUSDT",
        Symbol.IOST: "IOSTUSDT",
        Symbol.IOTA: "IOTAUSDT",
        Symbol.IOTX: "IOTXUSDT",
        Symbol.JASMY: "JASMYUSDT",
        Symbol.JST: "JSTUSDT",
        Symbol.KAVA: "KAVAUSDT",
        Symbol.KDA: "KDAUSDT",
        Symbol.KLAY: "KLAYUSDT",
        Symbol.KNC: "KNCUSDT",
        Symbol.KSM: "KSMUSDT",
        Symbol.LINA: "LINAUSDT",
        Symbol.LINK: "LINKUSDT",
        Symbol.LIT: "LITUSDT",
        Symbol.LOOKS: "LOOKSUSDT",
        Symbol.LPT: "LPTUSDT",
        Symbol.LRC: "LRCUSDT",
        Symbol.LTC: "LTCUSDT",
        Symbol.MANA: "MANAUSDT",
        Symbol.MASK: "MASKUSDT",
        Symbol.MATIC: "MATICUSDT",
        Symbol.MINA: "MINAUSDT",
        Symbol.MKR: "MKRUSDT",
        Symbol.MTL: "MTLUSDT",
        Symbol.NEAR: "NEARUSDT",
        Symbol.NEO: "NEOUSDT",
        Symbol.OCEAN: "OCEANUSDT",
        Symbol.OGN: "OGNUSDT",
        Symbol.OMG: "OMGUSDT",
        Symbol.ONE: "ONEUSDT",
        Symbol.PAXG: "PAXGUSDT",
        Symbol.PEOPLE: "PEOPLEUSDT",
        Symbol.QTUM: "QTUMUSDT",
        Symbol.RAY: "RAYUSDT",
        Symbol.REEF: "REEFUSDT",
        Symbol.REN: "RENUSDT",
        Symbol.REQ: "REQUSDT",
        Symbol.RNDR: "RNDRUSDT",
        Symbol.ROSE: "ROSEUSDT",
        Symbol.RSR: "RSRUSDT",
        Symbol.RSS3: "RSS3USDT",
        Symbol.RUNE: "RUNEUSDT",
        Symbol.RVN: "RVNUSDT",
        Symbol.SAND: "SANDUSDT",
        Symbol.SC: "SCUSDT",
        Symbol.SCRT: "SCRTUSDT",
        Symbol.SFP: "SFPUSDT",
        Symbol.SHIB1000: "SHIB1000USDT",
        Symbol.SKL: "SKLUSDT",
        Symbol.SLP: "SLPUSDT",
        Symbol.SNX: "SNXUSDT",
        Symbol.SOL: "SOLUSDT",
        Symbol.SPELL: "SPELLUSDT",
        Symbol.SRM: "SRMUSDT",
        Symbol.STMX: "STMXUSDT",
        Symbol.STORJ: "STORJUSDT",
        Symbol.STX: "STXUSDT",
        Symbol.SUN: "SUNUSDT",
        Symbol.SUSHI: "SUSHIUSDT",
        Symbol.SXP: "SXPUSDT",
        Symbol.THETA: "THETAUSDT",
        Symbol.TLM: "TLMUSDT",
        Symbol.TOMO: "TOMOUSDT",
        Symbol.TRX: "TRXUSDT",
        Symbol.UNI: "UNIUSDT",
        Symbol.VET: "VETUSDT",
        Symbol.WAVES: "WAVESUSDT",
        Symbol.WOO: "WOOUSDT",
        Symbol.XCN: "XCNUSDT",
        Symbol.XEM: "XEMUSDT",
        Symbol.XLM: "XLMUSDT",
        Symbol.XMR: "XMRUSDT",
        Symbol.XRP: "XRPUSDT",
        Symbol.XTZ: "XTZUSDT",
        Symbol.YFI: "YFIUSDT",
        Symbol.YGG: "YGGUSDT",
        Symbol.ZEC: "ZECUSDT",
        Symbol.ZEN: "ZENUSDT",
        Symbol.ZIL: "ZILUSDT",
        Symbol.ZRX: "ZRXUSDT",
    },
}
