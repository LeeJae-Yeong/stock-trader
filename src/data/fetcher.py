"""주식 데이터 수집 - FinanceDataReader 사용 (한국 주식, 무료)"""
from datetime import datetime, timedelta

import pandas as pd

try:
    import FinanceDataReader as fdr
except ImportError:
    fdr = None


def fetch_stock_data(symbol: str, days: int = 120) -> pd.DataFrame | None:
    """
    개별 종목 시세 조회
    symbol: 종목코드 (예: '005930' 삼성전자, '000660' SK하이닉스)
    """
    if fdr is None:
        raise ImportError("FinanceDataReader 설치 필요: pip install FinanceDataReader")

    end = datetime.now()
    start = end - timedelta(days=days)

    try:
        df = fdr.DataReader(symbol, start, end)
        if df.empty:
            return None
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception:
        return None


def fetch_kospi_list() -> pd.DataFrame:
    """KOSPI 종목 리스트 조회"""
    if fdr is None:
        raise ImportError("FinanceDataReader 설치 필요")
    return fdr.StockListing("KOSPI")


def fetch_kosdaq_list() -> pd.DataFrame:
    """KOSDAQ 종목 리스트 조회"""
    if fdr is None:
        raise ImportError("FinanceDataReader 설치 필요")
    return fdr.StockListing("KOSDAQ")


# 관심 종목 기본 리스트 (거래 활성 종목 위주)
DEFAULT_WATCHLIST: list[tuple[str, str]] = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("035420", "NAVER"),
    ("051910", "LG화학"),
    ("006400", "삼성SDI"),
    ("035720", "카카오"),
    ("005380", "현대차"),
    ("000270", "기아"),
    ("105560", "KB금융"),
    ("055550", "신한지주"),
    ("032830", "삼성생명"),
    ("068270", "셀트리온"),
    ("207940", "삼성바이오로직스"),
    ("003670", "포스코퓨처엠"),
    ("373220", "LG에너지솔루션"),
]


def get_watchlist() -> list[tuple[str, str]]:
    """스크리닝 대상 종목 리스트 반환 (기본 관심종목 사용)"""
    return DEFAULT_WATCHLIST.copy()


# 샛별형 스크리닝용 종목 풀 (KOSDAQ + 중소형 KOSPI)
RISING_STAR_UNIVERSE: list[tuple[str, str]] = [
    # KOSDAQ 대표
    ("247540", "에코플라스틱"),
    ("086520", "에코프로"),
    ("367000", "플러스제넥스"),
    ("039200", "오스코텍"),
    ("041510", "에스엠"),
    ("317770", "엑스페릭스"),
    ("290670", "대오미에어"),
    ("900110", "이스트아시아홀딩스"),
    ("109610", "이센스"),
    ("085370", "루트로닉"),
    ("214150", "클래시스"),
    ("066970", "엘앤에프"),
    ("246960", "현우산업"),
    ("263750", "펄어비스"),
    ("196490", "디에이테크놀로지"),
    ("066700", "테라젠이텍스"),
    ("058970", "코마스"),
    ("053160", "프리엠스"),
    ("073010", "케이에스피"),
    # KOSPI 중소형
    ("042700", "한미반도체"),
    ("033180", "KH 필룩스"),
    ("103140", "풍산"),
    ("064960", "S&T모티브"),
    ("015890", "태경산업"),
    ("281820", "케이엔씨"),
    ("272210", "한화시스템"),
    ("241560", "두산에너빌리티"),
    ("034020", "두산에너지빌리티"),
    ("006880", "신송홀딩스"),
    ("042660", "한화오션"),
    ("009540", "한국조선해양"),
    ("004020", "현대제철"),
    ("017800", "현대엘리베이"),
    ("047040", "대우건설"),
]


def get_rising_star_universe(limit: int = 80) -> list[tuple[str, str]]:
    """샛별형 스크리닝 대상 종목 (KOSDAQ + 중소형 KOSPI)"""
    try:
        kospi = fetch_symbol_list("KOSPI", limit=150)
        kosdaq = fetch_symbol_list("KOSDAQ", limit=60)
        kospi_mid = kospi[50:100] if len(kospi) > 50 else kospi[30:]
        combined = kospi_mid + kosdaq[:60]
        seen = set()
        result = [(c, n) for c, n in combined if c not in seen and not seen.add(c)]
        return (result[:limit] if result else RISING_STAR_UNIVERSE.copy())[:limit]
    except Exception:
        return RISING_STAR_UNIVERSE.copy()[:limit]


def fetch_symbol_list(exchange: str = "KOSPI", limit: int = 100) -> list[tuple[str, str]]:
    """
    시장별 종목 리스트 조회 (KOSPI/KOSDAQ)
    Returns: [(종목코드, 종목명), ...]
    """
    try:
        if exchange == "KOSPI":
            df = fetch_kospi_list()
        else:
            df = fetch_kosdaq_list()

        if df is None or df.empty:
            return get_watchlist()[:limit]

        result = []
        for _, row in df.iterrows():
            code = str(row.get("Code", row.get("Symbol", "")))
            name = str(row.get("Name", ""))
            if code and code.isdigit():
                result.append((code, name))
            if len(result) >= limit:
                break
        return result if result else get_watchlist()[:limit]
    except Exception:
        return get_watchlist()[:limit]
