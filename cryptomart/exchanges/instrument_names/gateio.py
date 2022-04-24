from ...enums import InstrumentType, Symbol

instrument_names = {
    InstrumentType.PERPETUAL: {
        Symbol.CLV: "CLV_USDT",
        Symbol.AR: "AR_USDT",
        Symbol.IMX: "IMX_USDT",
        Symbol.MELON: "MELON_USDT",
        Symbol.FTT: "FTT_USDT",
        Symbol.SUSHI: "SUSHI_USDT",
        Symbol.BIT: "BIT_USDT",
        Symbol.ALT: "ALT_USDT",
        Symbol.NEAR: "NEAR_USDT",
        Symbol.YFI: "YFI_USDT",
        Symbol.ZEC: "ZEC_USDT",
        Symbol.RVN: "RVN_USDT",
        Symbol.BAND: "BAND_USDT",
        Symbol.XVS: "XVS_USDT",
        Symbol.NKN: "NKN_USDT",
        Symbol.REEF: "REEF_USDT",
        Symbol.OXY: "OXY_USDT",
        Symbol.BCH: "BCH_USDT",
        Symbol.WAVES: "WAVES_USDT",
        Symbol.CAKE: "CAKE_USDT",
        Symbol.ONE: "ONE_USDT",
        Symbol.ANC: "ANC_USDT",
        Symbol.ETH: "ETH_USDT",
        Symbol.CRV: "CRV_USDT",
        Symbol.MKISHU: "MKISHU_USDT",
        Symbol.COTI: "COTI_USDT",
        Symbol.FIL: "FIL_USDT",
        Symbol.PEOPLE: "PEOPLE_USDT",
        Symbol.MANA: "MANA_USDT",
        Symbol.IOTX: "IOTX_USDT",
        Symbol.WAXP: "WAXP_USDT",
        Symbol.ATOM: "ATOM_USDT",
        Symbol.HBAR: "HBAR_USDT",
        Symbol.MOVR: "MOVR_USDT",
        Symbol.BZZ: "BZZ_USDT",
        Symbol.KEEP: "KEEP_USDT",
        Symbol.KAVA: "KAVA_USDT",
        Symbol.OMG: "OMG_USDT",
        Symbol.UNI: "UNI_USDT",
        Symbol.GALA: "GALA_USDT",
        Symbol.AAVE: "AAVE_USDT",
        Symbol.LTC: "LTC_USDT",
        Symbol.CRU: "CRU_USDT",
        Symbol.STORJ: "STORJ_USDT",
        Symbol.XAUG: "XAUG_USDT",
        Symbol.GRIN: "GRIN_USDT",
        Symbol.SXP: "SXP_USDT",
        Symbol.IRIS: "IRIS_USDT",
        Symbol.RAY: "RAY_USDT",
        Symbol.ALPHA: "ALPHA_USDT",
        Symbol.BNB: "BNB_USDT",
        Symbol.CKB: "CKB_USDT",
        Symbol.CERE: "CERE_USDT",
        Symbol.POLY: "POLY_USDT",
        Symbol.NEST: "NEST_USDT",
        Symbol.OKB: "OKB_USDT",
        Symbol.OGN: "OGN_USDT",
        Symbol.TLM: "TLM_USDT",
        Symbol.DOT: "DOT_USDT",
        Symbol.TONCOIN: "TONCOIN_USDT",
        Symbol.BTM: "BTM_USDT",
        Symbol.TRIBE: "TRIBE_USDT",
        Symbol.THETA: "THETA_USDT",
        Symbol.ADA: "ADA_USDT",
        Symbol.BTC: "BTC_USDT",
        Symbol.AMPL: "AMPL_USDT",
        Symbol.ANKR: "ANKR_USDT",
        Symbol.ANT: "ANT_USDT",
        Symbol.TRX: "TRX_USDT",
        Symbol.YFII: "YFII_USDT",
        Symbol.MTL: "MTL_USDT",
        Symbol.MBABYDOGE: "MBABYDOGE_USDT",
        Symbol.SAND: "SAND_USDT",
        Symbol.SUN: "SUN_USDT",
        Symbol.SERO: "SERO_USDT",
        Symbol.BEAM: "BEAM_USDT",
        Symbol.SRM: "SRM_USDT",
        Symbol.RAD: "RAD_USDT",
        Symbol.BAT: "BAT_USDT",
        Symbol.KSM: "KSM_USDT",
        Symbol.SOL: "SOL_USDT",
        Symbol.AXS: "AXS_USDT",
        Symbol.MAKITA: "MAKITA_USDT",
        Symbol.BCD: "BCD_USDT",
        Symbol.BNT: "BNT_USDT",
        Symbol.QTUM: "QTUM_USDT",
        Symbol.AVAX: "AVAX_USDT",
        Symbol.SNX: "SNX_USDT",
        Symbol.EOS: "EOS_USDT",
        Symbol.MKR: "MKR_USDT",
        Symbol.PERP: "PERP_USDT",
        Symbol.XRP: "XRP_USDT",
        Symbol.ZKS: "ZKS_USDT",
        Symbol.GITCOIN: "GITCOIN_USDT",
        Symbol.COMP: "COMP_USDT",
        Symbol.WSB: "WSB_USDT",
        Symbol.LINK: "LINK_USDT",
        Symbol.MATIC: "MATIC_USDT",
        Symbol.CFX: "CFX_USDT",
        Symbol.ONT: "ONT_USDT",
        Symbol.CHR: "CHR_USDT",
        Symbol.LINA: "LINA_USDT",
        Symbol.MBOX: "MBOX_USDT",
        Symbol.DASH: "DASH_USDT",
        Symbol.DYDX: "DYDX_USDT",
        Symbol.ETC: "ETC_USDT",
        Symbol.HT: "HT_USDT",
        Symbol.LUNA: "LUNA_USDT",
        Symbol.MASK: "MASK_USDT",
        Symbol.LON: "LON_USDT",
        Symbol.JST: "JST_USDT",
        Symbol.PEARL: "PEARL_USDT",
        Symbol.SKL: "SKL_USDT",
        Symbol.CONV: "CONV_USDT",
        Symbol.TFUEL: "TFUEL_USDT",
        Symbol.XLM: "XLM_USDT",
        Symbol.GRT: "GRT_USDT",
        Symbol.NU: "NU_USDT",
        Symbol.FTM: "FTM_USDT",
        Symbol.TRU: "TRU_USDT",
        Symbol.JASMY: "JASMY_USDT",
        Symbol.HIVE: "HIVE_USDT",
        Symbol.EXCH: "EXCH_USDT",
        Symbol.LPT: "LPT_USDT",
        Symbol.ROSE: "ROSE_USDT",
        Symbol.ALGO: "ALGO_USDT",
        Symbol.SUPER: "SUPER_USDT",
        Symbol.SHIB: "SHIB_USDT",
        Symbol.ENJ: "ENJ_USDT",
        Symbol.BTS: "BTS_USDT",
        Symbol.BSV: "BSV_USDT",
        Symbol.FLOW: "FLOW_USDT",
        Symbol.RUNE: "RUNE_USDT",
        Symbol.CHZ: "CHZ_USDT",
        Symbol.DOGE: "DOGE_USDT",
        Symbol.BADGER: "BADGER_USDT",
        Symbol._1INCH: "1INCH_USDT",
        Symbol.PRIV: "PRIV_USDT",
        Symbol.CSPR: "CSPR_USDT",
        Symbol.C98: "C98_USDT",
        Symbol.RACA: "RACA_USDT",
        Symbol.CELR: "CELR_USDT",
        Symbol.DEFI: "DEFI_USDT",
        Symbol.XEM: "XEM_USDT",
        Symbol.ALICE: "ALICE_USDT",
        Symbol.XEC: "XEC_USDT",
        Symbol.ICP: "ICP_USDT",
        Symbol.ENS: "ENS_USDT",
        Symbol.LRC: "LRC_USDT",
        Symbol.POND: "POND_USDT",
        Symbol.BAKE: "BAKE_USDT",
        Symbol.CRO: "CRO_USDT",
        Symbol.CVC: "CVC_USDT",
        Symbol.LIT: "LIT_USDT",
        Symbol.MINA: "MINA_USDT",
        Symbol.ZIL: "ZIL_USDT",
        Symbol.XMR: "XMR_USDT",
        Symbol.FRONT: "FRONT_USDT",
        Symbol.CTSI: "CTSI_USDT",
        Symbol.IOST: "IOST_USDT",
        Symbol.ZEN: "ZEN_USDT",
        Symbol.REQ: "REQ_USDT",
        Symbol.RNDR: "RNDR_USDT",
        Symbol.VRA: "VRA_USDT",
        Symbol.YGG: "YGG_USDT",
        Symbol.DEGO: "DEGO_USDT",
        Symbol.ARPA: "ARPA_USDT",
        Symbol.XTZ: "XTZ_USDT",
        Symbol.EGLD: "EGLD_USDT",
        Symbol.POLS: "POLS_USDT",
        Symbol.VET: "VET_USDT",
        Symbol.XCH: "XCH_USDT",
        Symbol.NFT: "NFT_USDT",
        Symbol.BICO: "BICO_USDT",
        Symbol.SLP: "SLP_USDT",
        Symbol.ACH: "ACH_USDT",
    }
}