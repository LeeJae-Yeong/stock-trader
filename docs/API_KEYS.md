# API 키 설정 가이드

주식 트레이더 프로그램에 필요한 API 키 발급 및 설정 방법입니다.

---

## 1. 한국투자증권 Open API (KIS)

**용도**: 국내 주식 시세 조회, 주문 (모의/실전)

### 발급 방법

1. [한국투자증권 API 포털](https://apiportal.koreainvestment.com/) 접속
2. 회원가입 후 로그인
3. **앱 등록** → 새 앱 생성
4. `APP KEY`, `APP SECRET` 발급
5. 계좌번호(`CANO`), 계좌상품코드(`ACNT_PRDT_CD`) 확인

### 필요한 값

| 변수명 | 설명 | 예시 |
|--------|------|------|
| KIS_APP_KEY | 앱 키 | `PSxxxxxxxxxxxx` |
| KIS_APP_SECRET | 앱 시크릿 | `xxxxxxxxxxxxxxxx` |
| KIS_BASE_URL | API 기본 URL (모의/실전 구분) | 모의: `https://openapivts.koreainvestment.com:29443` |
| KIS_CANO | 계좌번호 8자리 | `12345678` |
| KIS_ACNT_PRDT_CD | 계좌상품코드 2자리 | `01` |

### URL 구분

- **모의투자**: `https://openapivts.koreainvestment.com:29443`
- **실전투자**: `https://openap.real.koreainvestment.com:9443`

---

## 2. OpenAI API

**용도**: AI 기반 분석, 뉴스 요약, LLM 연동

### 발급 방법

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 회원가입/로그인
3. **API Keys** → Create new secret key

### 필요한 값

| 변수명 | 설명 |
|--------|------|
| OPENAI_API_KEY | `sk-` 로 시작하는 API 키 |

---

## 3. 설정 적용

```bash
# env.example을 복사
cp env.example .env

# .env 파일을 편집하여 실제 키 입력
```

---

## 보안 주의사항

- `.env` 파일은 **절대** Git에 커밋하지 마세요.
- API 키가 노출되었다면 즉시 재발급하세요.
- 실전 거래용 키는 별도 관리하고, 모의투자로 충분히 검증 후 사용하세요.
