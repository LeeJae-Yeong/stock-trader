"""
모바일 웹앱 - 조회 버튼으로 추천 확인
실행: python webapp.py  또는  flask run
배포 후 아이폰 Safari에서 열고 "홈 화면에 추가" → 앱처럼 사용
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, jsonify, render_template_string, request

from main import run_rising_star_recommender, run_trend_recommender

app = Flask(__name__)

# 결과 캐시 (5분간 유지)
_cache = {"data": None, "time": None}
CACHE_MIN = 5


def get_recommendations(fast_mode: bool = True):
    """추천 실행 (fast=True: 샛별 8종목 스캔, Render 30초 제한 대응)"""
    global _cache
    if _cache["data"] and _cache["time"]:
        elapsed = (datetime.now() - _cache["time"]).total_seconds()
        if elapsed < CACHE_MIN * 60:
            return _cache["data"]

    trend = run_trend_recommender()
    rising = run_rising_star_recommender(limit=8) if fast_mode else run_rising_star_recommender()

    data = {
        "trend": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "price": int(r.current_price),
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
    }
    _cache = {"data": data, "time": datetime.now()}
    return data


HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>주식 추천</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,sans-serif;padding:16px;background:#1a1a2e;color:#eee;min-height:100vh}
h1{font-size:18px;margin-bottom:12px;color:#fff}
.btn{display:block;width:100%;padding:18px;font-size:18px;font-weight:600;background:#00d9ff;color:#1a1a2e;border:none;border-radius:12px;cursor:pointer;margin-bottom:16px}
.btn:active{opacity:.9}
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
</style>
</head>
<body>
<h1>주식 추천</h1>
<button class="btn" id="btn" onclick="run()">조회</button>
<div id="out"></div>
<p class="caption">토스증권 앱에서 수동 매매 · 참고용</p>
<script>
async function run(){
  var btn=document.getElementById('btn');
  var out=document.getElementById('out');
  btn.disabled=true;
  out.innerHTML='<div class="loading">분석 중... 20~30초 소요</div>';
  try{
    var r=await fetch('/api/run');
    var d=await r.json();
    var h='';
    h+='<div class="section">추세 기반</div>';
    for(var x of d.trend){
      var c='tag-buy';if(x.signal==='관망')c='tag-watch';if(x.signal==='주의')c='tag-warn';
      h+='<div class="card"><span class="tag '+c+'">'+x.signal+'</span><span class="symbol">['+x.symbol+'] '+x.name+'</span><p class="price">'+x.price.toLocaleString()+'원 · 점수 '+x.score+'</p><ul>';
      for(var rr of x.reasons)h+='<li>'+rr+'</li>';
      h+='</ul></div>';
    }
    h+='<div class="section">샛별</div>';
    for(var x of d.rising){
      h+='<div class="card"><span class="tag tag-star">샛별</span><span class="symbol">['+x.symbol+'] '+x.name+'</span><p class="price">'+x.price.toLocaleString()+'원</p><ul>';
      for(var rr of x.reasons)h+='<li>'+rr+'</li>';
      h+='</ul></div>';
    }
    if(d.rising.length===0)h+='<div class="card">조건에 맞는 종목 없음</div>';
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
    full = request.args.get("full") == "1"
    data = get_recommendations(fast_mode=not full)
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
