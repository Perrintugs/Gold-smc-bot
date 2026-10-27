from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime
import threading, time, pytz
app = Flask(__name__)
bot = {"price":0, "session":"-", "bias":"-", "signal":"En attente London Open...", "ob":"-", "liquidity":"-"}
def get_data(interval):
    return yf.download("GC=F", period="5d", interval=interval, progress=False)
def get_session():
    tz = pytz.timezone("Africa/Douala")
    now = datetime.now(tz)
    h = now.hour
    if 1 <= h < 9: return "ASIE - NE PAS TRADER"
    elif 9 <= h < 13: return "LONDRES - KILL ZONE"
    elif 14 <= h < 18: return "NEW YORK - KILL ZONE"
    else: return "HORS SESSION"
def smc_pro():
    while True:
        try:
            df_m15 = get_data("15m")
            df_m5 = get_data("5m")
            if len(df_m15) < 60: time.sleep(60); continue
            price = float(df_m15['Close'].iloc[-1])
            bot["price"] = round(price,2)
            bot["session"] = get_session()
            if "NE PAS" in bot["session"] or "HORS" in bot["session"]:
                bot["signal"] = f"{bot['session']} - On attend. GOLD {price:.2f}"
                time.sleep(60); continue
            last_high = float(df_m15['High'].iloc[-51:-1].max())
            last_low = float(df_m15['Low'].iloc[-51:-1].min())
            close = float(df_m15['Close'].iloc[-2])
            if close > last_high:
                bot["bias"]="HAUSSIER BUY"
                for i in range(2,40):
                    o=float(df_m15['Open'].iloc[-i]); c=float(df_m15['Close'].iloc[-i])
                    if c < o:
                        ob_l=float(df_m15['Low'].iloc[-i]); ob_h=float(df_m15['High'].iloc[-i])
                        bot["ob"]=f"OB BUY {ob_l:.2f}-{ob_h:.2f}"
                        if ob_l <= price <= ob_h:
                            c1=float(df_m5['Close'].iloc[-1]); o1=float(df_m5['Open'].iloc[-1])
                            if c1 > o1:
                                sl=ob_l-3; tp=price + (price-sl)*3
                                bot["signal"]=f"BUY GOLD | Entree {price:.2f} | SL {sl:.2f} | TP {tp:.2f}"
                        break
            elif close < last_low:
                bot["bias"]="BAISSIER SELL"
                for i in range(2,40):
                    o=float(df_m15['Open'].iloc[-i]); c=float(df_m15['Close'].iloc[-i])
                    if c > o:
                        ob_l=float(df_m15['Low'].iloc[-i]); ob_h=float(df_m15['High'].iloc[-i])
                        bot["ob"]=f"OB SELL {ob_l:.2f}-{ob_h:.2f}"
                        if ob_l <= price <= ob_h:
                            c1=float(df_m5['Close'].iloc[-1]); o1=float(df_m5['Open'].iloc[-1])
                            if c1 < o1:
                                sl=ob_h+3; tp=price - (sl-price)*3
                                bot["signal"]=f"SELL GOLD | Entree {price:.2f} | SL {sl:.2f} | TP {tp:.2f}"
                        break
            else: bot["bias"]="RANGE"
        except Exception as e: bot["signal"]=f"Erreur {e}"
        time.sleep(60)
threading.Thread(target=smc_pro, daemon=True).start()
HTML = """<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#070c19;color:#fff;font-family:sans-serif;padding:12px}.card{background:#121b32;border:1px solid #2a3d6a;border-radius:16px;padding:16px;margin-bottom:12px}.price{font-size:34px;font-weight:800;color:#f5d76e}.sess{color:#00ff88;font-weight:bold}.sig{font-size:17px;background:#1e2d52;padding:14px;border-radius:12px}</style></head><body><h2>GOLD SMC PRO</h2><div class="card"><div class="price">${{price}}</div><div class="sess">{{session}}</div><div>{{bias}}</div><div>OB: {{ob}}</div></div><div class="card"><b>SIGNAL:</b><div class="sig">{{signal}}</div></div><script>setTimeout(()=>location.reload(),10000)</script></body></html>"""
@app.route("/")
def home(): return render_template_string(HTML, price=bot["price"], session=bot["session"], bias=bot["bias"], ob=bot["ob"], signal=bot["signal"])
app.run(host="0.0.0.0", port=10000)                                 
