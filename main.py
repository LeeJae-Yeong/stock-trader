"""
주식 추천 시스템 실행
- 기술적 지표 기반 추천
- 토스증권 앱에서 수동 매수/매도 진행
"""
import io
import sys
from pathlib import Path

# Windows 콘솔 한글 출력
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data import (
    fetch_stock_data,
    get_market_scan_universe,
    get_rising_star_universe,
    get_watchlist,
)
from src.recommender import (
    Recommendation,
    evaluate_rising_star,
    evaluate_stock,
)


def run_trend_recommender(
    market: str = "kr", scope: str = "watchlist"
) -> list[Recommendation]:
    """추세 기반 스크리닝. market: 'kr'|'us', scope: 'watchlist'|'market'"""
    if scope == "market":
        watchlist = get_market_scan_universe(market=market, limit=25)
    else:
        watchlist = get_watchlist(market=market)
    results: list[Recommendation] = []

    for symbol, name in watchlist:
        df = fetch_stock_data(symbol, days=120)
        rec = evaluate_stock(df, symbol, name)
        if rec:
            results.append(rec)
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def run_rising_star_recommender(limit: int = 80) -> list[Recommendation]:
    """샛별형 스크리닝 (거래량 급증, 고점 돌파, 모멘텀)"""
    universe = get_rising_star_universe(limit=limit)
    results: list[Recommendation] = []

    for symbol, name in universe:
        df = fetch_stock_data(symbol, days=120)
        rec = evaluate_rising_star(df, symbol, name)
        if rec and rec.signal == "샛별":
            results.append(rec)
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def run_recommender() -> None:
    """전체 추천 실행"""
    print("=" * 60)
    print("주식 추천 시스템 (토스증권 수동 매매용)")
    print("=" * 60)

    # 1. 추세 기반
    print("\n[1] 추세 기반 추천 (관심종목)")
    print("-" * 60)
    trend_results = run_trend_recommender()
    for rec in trend_results:
        tag = "[매수]" if rec.signal == "매수" else "[관망]" if rec.signal == "관망" else "[주의]"
        print(f"\n{tag} [{rec.symbol}] {rec.name}")
        print(f"   현재가: {rec.current_price:,.0f}원 | 점수: {rec.score}")
        for r in rec.reasons[:3]:
            print(f"   - {r}")

    # 2. 떠오르는 샛별
    print("\n\n[2] 떠오르는 샛별")
    print("-" * 60)
    rising_results = run_rising_star_recommender()
    if rising_results:
        for rec in rising_results[:15]:  # 상위 15개
            print(f"\n[샛별] [{rec.symbol}] {rec.name}")
            print(f"   현재가: {rec.current_price:,.0f}원 | 점수: {rec.score}")
            for r in rec.reasons[:4]:
                print(f"   - {r}")
    else:
        print("   조건에 맞는 종목이 없습니다.")


if __name__ == "__main__":
    run_recommender()
    print("\n" + "=" * 60)
    print("※ 위 추천은 참고용이며, 투자 책임은 본인에게 있습니다.")
    print("※ 토스증권 앱에서 직접 매수/매도해 주세요.")
    print("=" * 60)
