"""추천 로직 - 기술적 지표 기반 스크리닝"""
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass


@dataclass
class Recommendation:
    """추천 결과"""
    symbol: str
    name: str
    current_price: float
    score: float
    reasons: list[str]
    signal: str  # "매수", "관망", "주의", "샛별"
    category: str = "trend"  # "trend" | "rising_star"


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """이동평균선, RSI 등 기술적 지표 추가"""
    if df is None or df.empty or len(df) < 20:
        return df

    df = df.copy()
    # 컬럼명 정규화 (Close, close 등)
    close_col = "Close" if "Close" in df.columns else "close"
    high_col = "High" if "High" in df.columns else "high"
    low_col = "Low" if "Low" in df.columns else "low"

    if close_col not in df.columns:
        return df

    # 이동평균선
    df["ma5"] = df[close_col].rolling(5).mean()
    df["ma20"] = df[close_col].rolling(20).mean()
    df["ma60"] = df[close_col].rolling(60).mean()

    # RSI (14일)
    try:
        import ta

        delta = df[close_col].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        df["rsi"] = 100 - (100 / (1 + rs))
    except ImportError:
        df["rsi"] = 50  # ta 미설치 시 중립값

    # 거래량 평균
    vol_col = "Volume" if "Volume" in df.columns else "volume"
    if vol_col in df.columns:
        df["vol_ma20"] = df[vol_col].rolling(20).mean()
    return df


def evaluate_stock(
    df: pd.DataFrame | None, symbol: str, name: str
) -> Recommendation | None:
    """
    개별 종목 평가
    - 골든크로스(5일선 > 20일선) 가산
    - RSI 과매도(30 미만) 구간 매수 유리
    - RSI 과매수(70 초과) 주의
    """
    if df is None or df.empty or len(df) < 20:
        return None

    df = add_technical_indicators(df)

    close_col = "Close" if "Close" in df.columns else "close"
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else latest

    current_price = float(latest[close_col])
    score = 0.0
    reasons = []

    # 1. 골든크로스 (5일선 > 20일선)
    ma5 = latest.get("ma5")
    ma20 = latest.get("ma20")
    if ma5 is not None and ma20 is not None and not (pd.isna(ma5) or pd.isna(ma20)):
        if ma5 > ma20:
            score += 2.0
            reasons.append("5일선 > 20일선 (단기 상승 추세)")
        else:
            reasons.append("5일선 < 20일선 (단기 횡보/하락)")

    # 2. 장기 추세 (20일선 > 60일선)
    ma60 = latest.get("ma60")
    if ma20 is not None and ma60 is not None and not (pd.isna(ma20) or pd.isna(ma60)):
        if ma20 > ma60:
            score += 1.0
            reasons.append("20일선 > 60일선 (장기 상승 추세)")

    # 3. RSI
    rsi = latest.get("rsi")
    if rsi is not None and not pd.isna(rsi):
        rsi = float(rsi)
        if rsi < 30:
            score += 1.5
            reasons.append(f"RSI {rsi:.0f} (과매도 구간, 반등 가능)")
        elif rsi < 50:
            score += 0.5
            reasons.append(f"RSI {rsi:.0f} (중립偏低)")
        elif rsi > 70:
            score -= 1.0
            reasons.append(f"RSI {rsi:.0f} (과매수 구간, 조정 주의)")
        else:
            reasons.append(f"RSI {rsi:.0f} (중립)")

    # 4. 가격 위치 (현재가 vs 20일선)
    if ma20 is not None and not pd.isna(ma20):
        pct_from_ma20 = (current_price - ma20) / ma20 * 100
        if -3 < pct_from_ma20 < 5:
            score += 0.5
            reasons.append(f"20일선 대비 {pct_from_ma20:+.1f}% (적정 구간)")
        elif pct_from_ma20 < -5:
            reasons.append(f"20일선 대비 {pct_from_ma20:+.1f}% (저평가 구간)")

    # 신호 판정
    if score >= 3.5:
        signal = "매수"
    elif score >= 2.0:
        signal = "관망"
    else:
        signal = "주의"

    return Recommendation(
        symbol=symbol,
        name=name,
        current_price=current_price,
        score=round(score, 1),
        reasons=reasons,
        signal=signal,
        category="trend",
    )


def evaluate_rising_star(
    df: pd.DataFrame | None, symbol: str, name: str
) -> Recommendation | None:
    """
    떠오르는 샛별형 종목 평가
    - 거래량 급증 (2배 이상)
    - 20일 고점 돌파
    - 단기 모멘텀 (5일/10일 상승률)
    - RSI 과매수 아님 (성장 여력)
    """
    if df is None or df.empty or len(df) < 20:
        return None

    df = add_technical_indicators(df)
    close_col = "Close" if "Close" in df.columns else "close"
    vol_col = "Volume" if "Volume" in df.columns else "volume"

    latest = df.iloc[-1]
    current_price = float(latest[close_col])
    score = 0.0
    reasons = []

    # 1. 거래량 급증 (최근 5일 평균 vs 20일 평균)
    vol_ma5 = df[vol_col].tail(5).mean() if vol_col in df.columns else 0
    vol_ma20 = latest.get("vol_ma20")
    if vol_ma20 and vol_ma20 > 0 and vol_ma5 > 0:
        vol_ratio = vol_ma5 / vol_ma20
        if vol_ratio >= 2.0:
            score += 2.5
            reasons.append(f"거래량 급증 (5일평균/20일평균 {vol_ratio:.1f}배)")
        elif vol_ratio >= 1.5:
            score += 1.5
            reasons.append(f"거래량 증가 (5일평균/20일평균 {vol_ratio:.1f}배)")
        elif vol_ratio >= 1.2:
            score += 0.5
            reasons.append(f"거래량 소폭 증가 ({vol_ratio:.1f}배)")

    # 2. 20일 고점 돌파
    high_col = "High" if "High" in df.columns else "high"
    high_20d = df[high_col].tail(20).max()
    if current_price >= high_20d * 0.998:
        score += 2.0
        reasons.append("20일 고점 돌파 (신고가)")
    else:
        pct_to_high = (high_20d - current_price) / current_price * 100
        if pct_to_high < 3:
            score += 1.0
            reasons.append(f"20일 고점 근접 (약 {pct_to_high:.1f}% 남음)")

    # 3. 단기 모멘텀 (5일 상승률)
    if len(df) >= 6:
        close_5d_ago = float(df.iloc[-6][close_col])
        if close_5d_ago > 0:
            mom_5d = (current_price - close_5d_ago) / close_5d_ago * 100
            if mom_5d >= 10:
                score += 1.5
                reasons.append(f"5일 상승률 +{mom_5d:.1f}% (강한 모멘텀)")
            elif mom_5d >= 5:
                score += 1.0
                reasons.append(f"5일 상승률 +{mom_5d:.1f}%")
            elif mom_5d >= 0:
                reasons.append(f"5일 상승률 +{mom_5d:.1f}%")
            else:
                reasons.append(f"5일 상승률 {mom_5d:.1f}% (보합)")

    # 4. RSI (과매수 아닐 때 가산)
    rsi = latest.get("rsi")
    if rsi is not None and not pd.isna(rsi):
        rsi = float(rsi)
        if 40 <= rsi <= 65:
            score += 1.0
            reasons.append(f"RSI {rsi:.0f} (성장 여력 구간)")
        elif rsi < 40:
            score += 0.5
            reasons.append(f"RSI {rsi:.0f} (저평가, 반등 가능)")
        elif rsi > 75:
            score -= 0.5
            reasons.append(f"RSI {rsi:.0f} (과매수, 조정 리스크)")

    # 5. 5일선 > 20일선 (상승 추세)
    ma5 = latest.get("ma5")
    ma20 = latest.get("ma20")
    if ma5 is not None and ma20 is not None and not (pd.isna(ma5) or pd.isna(ma20)):
        if ma5 > ma20:
            score += 0.5
            reasons.append("5일선 > 20일선 (단기 상승)")

    # 신호: 점수 4.0 이상만 샛별 추천
    if score >= 5.0:
        signal = "샛별"
    elif score >= 4.0:
        signal = "샛별"
    elif score >= 3.0:
        signal = "관망"
    else:
        signal = "주의"

    return Recommendation(
        symbol=symbol,
        name=name,
        current_price=current_price,
        score=round(score, 1),
        reasons=reasons,
        signal=signal,
        category="rising_star",
    )
