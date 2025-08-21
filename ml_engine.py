# main.py i?inde karar
df = klines_to_df(ex.klines(limit=600))   # kendin df ?evir
ta_sig = ta_engine.decide(kl)             # ("LONG"/"SHORT", entry)
ml_sig = ml_engine.decide(df)             # ("LONG"/"SHORT", p)
news = news_engine.bias()                 # ("LONG"/"SHORT", conf)

# Rejim & vol filtreleri
trdir, vol = regime.allow(df)
cooldown.tick()

direction, entry = None, None
if ta_sig:
    direction, entry = ta_sig
    conf = 0.5
    if ml_sig and ml_sig[0]==direction: conf += 0.2*ml_sig[1]
    if news  and news[0]==direction:    conf += 0.2*news[1]
    # Rejim filtresi
    if (trdir==1 and direction=="SHORT") or (trdir==-1 and direction=="LONG"):
        conf -= 0.3
    if vol<df["close"].pct_change().rolling(50).std().median(): conf -= 0.1

    if conf>=0.65 and cooldown.ok() and pos_mgr.can_open(direction):
        sl,tp = atr_levels(df, entry, direction)
        execu.open_trade(direction, entry, sl, tp)
        pos_mgr.on_open(direction)
        cooldown.trigger()
