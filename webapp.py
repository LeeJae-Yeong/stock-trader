"""
모바일 웹앱 - 한국/미국 주식 추천, 탭 구분
실행: python webapp.py  또는  flask run
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, jsonify, render_template_string, request

from main import run_rising_star_recommender, run_trend_recommender

app = Flask(__name__)

# 캐시 (market_scope 키, 5분)
_cache: dict = {}
CACHE_MIN = 5


def _cache_key(market: str, scope: str) -> str:
    return f"{market}_{scope}"


def get_recommendations(
    market: str = "kr", scope: str = "watchlist", fast_mode: bool = True
):
    """추천 실행. market: 'kr'|'us', scope: 'watchlist'|'market'"""
    global _cache
    key = _cache_key(market, scope)
    if key not in _cache:
        _cache[key] = {"data": None, "time": None}
    c = _cache[key]
    if c["data"] and c["time"]:
        elapsed = (datetime.now() - c["time"]).total_seconds()
        if elapsed < CACHE_MIN * 60:
            out = c["data"].copy()
            out["updated_at"] = c["time"].strftime("%Y-%m-%d %H:%M")
            return out

    trend = run_trend_recommender(market=market, scope=scope)
    currency = "USD" if market == "us" else "KRW"

    # 샛별: 한국 + 관심종목일 때만 (시장 스캔은 추세만, 시간 제한)
    rising = []
    if market == "kr" and scope == "watchlist":
        rising = run_rising_star_recommender(limit=8) if fast_mode else run_rising_star_recommender()

    now = datetime.now()
    data = {
        "market": market,
        "scope": scope,
        "currency": currency,
        "trend": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "price": round(r.current_price, 2) if currency == "USD" else int(r.current_price),
                "score": r.score,
                "signal": r.signal,
                "reasons": r.reasons[:3],
            }
            for r in trend
        ],
        "rising": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "price": int(r.current_price),
                "score": r.score,
                "reasons": r.reasons[:4],
            }
            for r in rising[:10]
        ],
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
    }
    _cache[key] = {"data": data, "time": now}
    return data


HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>주식 추천</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,sans-serif;padding:16px;background:#1a1a2e;color:#eee;min-height:100vh}
h1{font-size:18px;margin-bottom:12px;color:#fff}
.tabs{display:flex;margin-bottom:12px;gap:8px}
.tab{padding:10px 20px;border-radius:8px;border:1px solid #444;background:#16213e;color:#888;cursor:pointer;font-size:14px}
.tab.on{background:#00d9ff;color:#1a1a2e;border-color:#00d9ff}
.btn{display:block;width:100%;padding:18px;font-size:18px;font-weight:600;background:#00d9ff;color:#1a1a2e;border:none;border-radius:12px;cursor:pointer;margin-bottom:16px}
.btn:disabled{opacity:.6;cursor:wait}
.loading{text-align:center;padding:40px;font-size:14px;color:#888}
.card{background:#16213e;border-radius:10px;padding:14px;margin-bottom:10px}
.tag{display:inline-block;padding:4px 10px;border-radius:6px;font-size:12px;margin-right:8px}
.tag-buy{background:#00c853;color:#000}
.tag-watch{background:#ff9800;color:#000}
.tag-warn{background:#f44336;color:#fff}
.tag-star{background:#2196f3;color:#fff}
.symbol{font-weight:600;color:#00d9ff}
.price{font-size:14px;color:#aaa;margin:6px 0}
ul{margin:4px 0 0 18px;font-size:13px;color:#bbb}
.section{margin-top:20px;font-size:14px;color:#888;border-bottom:1px solid #333;padding-bottom:6px}
.caption{font-size:11px;color:#555;margin-top:20px}
.updated{font-size:12px;color:#00d9ff;margin:12px 0;padding:8px 12px;background:rgba(0,217,255,.1);border-radius:8px}
.panel{display:none}
.panel.on{display:block}
</style>
</head>
<body>
<h1>주식 추천</h1>
<div class="tabs">
  <button class="tab on" id="tabKr" onclick="setTab('kr')">한국</button>
  <button class="tab" id="tabUs" onclick="setTab('us')">미국</button>
</div>
<div class="tabs" style="margin-bottom:8px">
  <button class="tab on" id="scopeWatch" onclick="setScope('watchlist')">관심종목</button>
  <button class="tab" id="scopeMarket" onclick="setScope('market')">시장 스캔</button>
</div>
<button class="btn" id="btn" onclick="run()">조회</button>
<div id="out"></div>
<p class="caption">토스증권 앱에서 수동 매매 · 참고용</p>
<script>
var currentMarket='kr';
var currentScope='watchlist';
function setTab(m){
  currentMarket=m;
  document.getElementById('tabKr').classList.toggle('on',m==='kr');
  document.getElementById('tabUs').classList.toggle('on',m==='us');
  document.getElementById('out').innerHTML='';
}
function setScope(s){
  currentScope=s;
  document.getElementById('scopeWatch').classList.toggle('on',s==='watchlist');
  document.getElementById('scopeMarket').classList.toggle('on',s==='market');
  document.getElementById('out').innerHTML='';
}
function fmtPrice(p, currency){
  if(currency==='USD') return '$'+Number(p).toLocaleString('en-US',{minimumFractionDigits:2});
  return Number(p).toLocaleString()+'원';
}
async function run(){
  var btn=document.getElementById('btn');
  var out=document.getElementById('out');
  btn.disabled=true;
  var scopeLabel=currentScope==='market'?'시장 스캔(약 25종)':'관심종목';
  out.innerHTML='<div class="loading">'+scopeLabel+' 분석 중... 25~35초 소요</div>';
  try{
    var r=await fetch('/api/run?market='+currentMarket+'&scope='+currentScope);
    var d=await r.json();
    var h='';
    if(d.updated_at) h='<p class="updated">5분 단위 갱신 · 마지막 갱신: '+d.updated_at+(d.scope==='market'?' (시장 스캔)':'')+'</p>';
    h+='<div class="section">추세 기반'+(d.scope==='market'?' · 시장 스캔 (일부 종목)':'')+'</div>';
    for(var x of d.trend){
      var c='tag-buy';if(x.signal==='관망')c='tag-watch';if(x.signal==='주의')c='tag-warn';
      h+='<div class="card"><span class="tag '+c+'">'+x.signal+'</span><span class="symbol">['+x.symbol+'] '+x.name+'</span><p class="price">'+fmtPrice(x.price,d.currency)+' · 점수 '+x.score+'</p><ul>';
      for(var rr of x.reasons)h+='<li>'+rr+'</li>';
      h+='</ul></div>';
    }
    if(d.rising && d.rising.length>0){
      h+='<div class="section">샛별</div>';
      for(var x of d.rising){
        h+='<div class="card"><span class="tag tag-star">샛별</span><span class="symbol">['+x.symbol+'] '+x.name+'</span><p class="price">'+x.price.toLocaleString()+'원</p><ul>';
        for(var rr of x.reasons)h+='<li>'+rr+'</li>';
        h+='</ul></div>';
      }
    } else if(d.market==='kr') {
      h+='<div class="section">샛별</div><div class="card">조건에 맞는 종목 없음</div>';
    }
    out.innerHTML=h;
  }catch(e){out.innerHTML='<div class="loading">오류: '+e.message+'</div>'}
  btn.disabled=false;
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/run")
def api_run():
    market = request.args.get("market", "kr")
    scope = request.args.get("scope", "watchlist")
    if market not in ("kr", "us"):
        market = "kr"
    if scope not in ("watchlist", "market"):
        scope = "watchlist"
    full = request.args.get("full") == "1"
    data = get_recommendations(market=market, scope=scope, fast_mode=not full)
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
