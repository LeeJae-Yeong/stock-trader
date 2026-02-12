"""
추천 결과를 HTML 파일로 저장
생성된 report.html을 아이폰으로 전송(에어드롭 등) 후 Safari에서 열기
실행: python export_report.py
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from main import run_rising_star_recommender, run_trend_recommender


def rec_to_dict(r):
    return {
        "symbol": r.symbol,
        "name": r.name,
        "price": int(r.current_price),
        "score": r.score,
        "signal": r.signal,
        "reasons": r.reasons,
    }


def generate_html(trend, rising) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    trend_json = [rec_to_dict(r) for r in trend]
    rising_json = [rec_to_dict(r) for r in rising[:15]]

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=yes">
<title>주식 추천 | {now}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:12px;background:#f5f5f5;font-size:15px;line-height:1.5}}
h1{{font-size:18px;margin-bottom:8px;color:#333}}
h2{{font-size:16px;margin:16px 0 8px;color:#444;border-bottom:1px solid #ddd;padding-bottom:4px}}
.card{{background:#fff;border-radius:8px;padding:12px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.symbol{{font-weight:600;color:#0066cc}}
.price{{color:#333;margin:4px 0}}
.tag{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;margin-right:6px}}
.tag-buy{{background:#e8f5e9;color:#2e7d32}}
.tag-watch{{background:#fff3e0;color:#e65100}}
.tag-warn{{background:#ffebee;color:#c62828}}
.tag-star{{background:#e3f2fd;color:#1565c0}}
ul{{margin:6px 0 0 20px;font-size:14px;color:#555}}
.caption{{font-size:12px;color:#888;margin-top:16px}}
</style>
</head>
<body>
<h1>주식 추천</h1>
<p class="caption">생성: {now} · 토스증권 앱에서 수동 매매</p>

<h2>추세 기반 (매수/관망)</h2>
"""

    for r in trend_json:
        tag_class = "tag-buy" if r["signal"] == "매수" else "tag-watch" if r["signal"] == "관망" else "tag-warn"
        html += f'<div class="card"><span class="tag {tag_class}">{r["signal"]}</span>'
        html += f'<span class="symbol">[{r["symbol"]}] {r["name"]}</span>'
        html += f'<p class="price">{r["price"]:,}원 · 점수 {r["score"]}</p>'
        html += "<ul>"
        for reason in r["reasons"][:3]:
            html += f"<li>{reason}</li>"
        html += "</ul></div>"

    html += "<h2>떠오르는 샛별</h2>"
    if rising_json:
        for r in rising_json:
            html += f'<div class="card"><span class="tag tag-star">샛별</span>'
            html += f'<span class="symbol">[{r["symbol"]}] {r["name"]}</span>'
            html += f'<p class="price">{r["price"]:,}원 · 점수 {r["score"]}</p>'
            html += "<ul>"
            for reason in r["reasons"][:4]:
                html += f"<li>{reason}</li>"
            html += "</ul></div>"
    else:
        html += '<div class="card">조건에 맞는 종목이 없습니다.</div>'

    html += '<p class="caption">※ 참고용. 투자 책임은 본인에게 있습니다.</p></body></html>'
    return html


def main():
    print("추천 분석 중...")
    trend = run_trend_recommender()
    rising = run_rising_star_recommender()
    print(f"추세: {len(trend)}종목, 샛별: {len(rising)}종목")

    html = generate_html(trend, rising)
    out_path = Path(__file__).parent / "report.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"\n저장 완료: {out_path.absolute()}")
    print("→ 이 파일을 아이폰으로 에어드롭/공유 후 Safari에서 열기")


if __name__ == "__main__":
    main()
