# Stock Trader - 추천 시스템 (토스증권 수동매매용)

AI·기술적 지표 기반 주식 추천 시스템입니다. **토스증권 앱에서 수동으로 매수/매도**합니다.

## 기능

- **추세 기반**: 관심종목 기술적 지표 (이동평균선, RSI) → 매수/관망/주의
- **떠오르는 샛별**: KOSDAQ·중소형 위주, 거래량 급증 + 고점 돌파 + 모멘텀
- CLI 또는 Streamlit 대시보드로 결과 확인

## 설치

```bash
# 가상환경 생성 (권장)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt
```

## 사용법

### CLI 실행

```bash
python main.py
```

### 대시보드 실행

```bash
streamlit run app.py
```

브라우저에서 추천 결과를 확인할 수 있습니다.

### 아이폰에서 확인 (HTML 파일)

```bash
python export_report.py
```

`report.html` 파일이 생성됩니다. 이 파일을:
1. **에어드롭**: Mac → 아이폰
2. **이메일/카카오톡**: 본인에게 전송 후 아이폰에서 다운로드
3. **iCloud Drive/드롭박스**: 업로드 후 아이폰 앱에서 열기

→ **Safari**에서 열면 아이폰에서 추천 결과 확인 가능 (오프라인 가능)

### 아이폰 앱처럼 사용 (조회 버튼)

```bash
python webapp.py
```

PC에서 실행 후 **아이폰과 같은 WiFi**에서 Safari로 접속:
- PC IP 확인: `ipconfig` (Windows) / `ifconfig` (Mac)
- 예: `http://192.168.0.10:5000`

**조회** 버튼을 누르면 분석 후 결과 표시.

**홈 화면에 추가 (앱처럼):**
1. Safari에서 해당 주소 열기
2. 하단 **공유** 버튼 → **홈 화면에 추가**
3. 아이콘 생김 → 앱처럼 실행, 조회 버튼으로 확인

※ PC가 켜져 있고 webapp이 실행 중이어야 함.  
※ **외부 접속**: GitHub에 올린 뒤 [Render.com](https://render.com) 무료 배포 → `docs/DEPLOY_RENDER.md` 참고

## 추천 로직

### 추세 기반
- **5일선 > 20일선** (골든크로스) → 상승 추세 가산
- **20일선 > 60일선** → 장기 상승 추세
- **RSI < 30** → 과매도 구간, 반등 가능성
- **RSI > 70** → 과매수 구간, 조정 주의
- 점수 3.5 이상 → 매수, 2.0~3.5 → 관망, 그 외 → 주의

### 떠오르는 샛별
- **거래량 급증** (5일평균/20일평균 2배↑) → 돌파 모멘텀
- **20일 고점 돌파/근접** → 신고가 구간
- **5일 상승률** 10%↑ → 단기 모멘텀
- **RSI 40~65** → 성장 여력 (과매수 아님)
- 점수 4.0 이상 → 샛별 추천

## 종목 리스트 수정

- **추세 기반**: `src/data/fetcher.py` → `DEFAULT_WATCHLIST`
- **샛별형**: `src/data/fetcher.py` → `RISING_STAR_UNIVERSE` (기본 폴백용)

## 주의사항

- 추천은 **참고용**이며, 투자 책임은 본인에게 있습니다.
- 수익을 보장하지 않습니다.
- 토스증권 앱에서 직접 주문해 주세요.
