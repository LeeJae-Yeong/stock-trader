"""
Streamlit 대시보드 - 추천 결과 확인
실행: streamlit run app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.data import fetch_stock_data, get_rising_star_universe, get_watchlist
from src.recommender import (
    Recommendation,
    evaluate_rising_star,
    evaluate_stock,
)


def main():
    st.set_page_config(page_title="주식 추천 | 토스증권 수동매매", layout="wide")

    st.title("📊 주식 추천 시스템")
    st.caption("토스증권 앱에서 수동으로 매수/매도해 주세요")

    tab1, tab2, tab3 = st.tabs(["📈 추세 기반", "⭐ 떠오르는 샛별", "전체 보기"])

    with tab1:
        watchlist = get_watchlist()
        results: list[Recommendation] = []
        with st.spinner("종목 분석 중..."):
            for symbol, name in watchlist:
                df = fetch_stock_data(symbol, days=120)
                rec = evaluate_stock(df, symbol, name)
                if rec:
                    results.append(rec)
            results.sort(key=lambda r: r.score, reverse=True)

        buy_list = [r for r in results if r.signal == "매수"]
        watch_list = [r for r in results if r.signal == "관망"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("매수 추천", len(buy_list), "")
        with col2:
            st.metric("관망", len(watch_list), "")
        with col3:
            st.metric("분석 완료", len(results), "종목")

        st.subheader("🟢 매수 추천" if buy_list else "🟢 매수 추천 (없음)")
        for rec in buy_list:
            with st.expander(f"**[{rec.symbol}] {rec.name}** — {rec.current_price:,.0f}원 (점수: {rec.score})"):
                for r in rec.reasons:
                    st.write(f"• {r}")
                st.info("토스증권 앱에서 검색 후 매수 검토")

        st.subheader("🟡 관망")
        for rec in watch_list[:10]:
            with st.expander(f"[{rec.symbol}] {rec.name} — {rec.current_price:,.0f}원 (점수: {rec.score})"):
                for r in rec.reasons:
                    st.write(f"• {r}")

    with tab2:
        universe = get_rising_star_universe(limit=50)
        rising_results: list[Recommendation] = []
        with st.spinner("샛별 종목 스캔 중... (KOSDAQ·중소형 위주)"):
            for symbol, name in universe:
                df = fetch_stock_data(symbol, days=120)
                rec = evaluate_rising_star(df, symbol, name)
                if rec and rec.signal == "샛별":
                    rising_results.append(rec)
            rising_results.sort(key=lambda r: r.score, reverse=True)

        st.metric("샛별 추천", len(rising_results), "종목")
        st.caption("거래량 급증 + 고점 돌파 + 모멘텀 조건")

        if rising_results:
            for rec in rising_results[:15]:
                with st.expander(f"⭐ [{rec.symbol}] {rec.name} — {rec.current_price:,.0f}원 (점수: {rec.score})"):
                    for r in rec.reasons:
                        st.write(f"• {r}")
                    st.info("토스증권 앱에서 검색 후 매수 검토")
        else:
            st.info("조건에 맞는 샛별 종목이 없습니다. (거래량 급증 2배↑ + 20일 고점 돌파 등)")

    with tab3:
        st.write("추세 + 샛별 결과 통합")
        all_results = results + rising_results
        all_results.sort(key=lambda r: r.score, reverse=True)
        for rec in all_results:
            tag = "⭐" if rec.category == "rising_star" else "📈"
            st.write(f"{tag} [{rec.symbol}] {rec.name} — {rec.current_price:,.0f}원 | {rec.signal} | 점수 {rec.score}")

    st.divider()
    st.caption("※ 추천은 기술적 지표 기반 참고용이며, 투자 책임은 본인에게 있습니다.")


if __name__ == "__main__":
    main()
