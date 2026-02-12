# Render.com 배포 가이드

아이폰 등 어디서든 접속 가능하도록 Render.com에 무료 배포하는 방법입니다.

## 1. GitHub에 코드 올리기

```bash
# 프로젝트 폴더에서
git init
git add .
git commit -m "Initial commit"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/stock-trader.git
git branch -M main
git push -u origin main
```

## 2. Render.com에서 배포

1. [Render.com](https://render.com) 접속 → 회원가입 (GitHub으로 로그인 권장)

2. **Dashboard** → **New +** → **Web Service**

3. **Connect a repository**:
   - GitHub 선택 후 `stock-trader` 저장소 연결
   - (처음이면 GitHub 권한 요청 수락)

4. **설정** (자동으로 감지되지만 확인):
   - **Name**: `stock-trader` (원하는 이름)
   - **Region**: Singapore (한국에서 빠름) 또는 Oregon
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn webapp:app --bind 0.0.0.0:$PORT --timeout 120`

5. **Create Web Service** 클릭

6. 배포 완료까지 3~5분 대기

7. 완료 후 `https://stock-trader-xxxx.onrender.com` 형태의 URL 생성

## 3. 접속

- 생성된 URL을 아이폰 Safari에서 열기
- **조회** 버튼 탭 → 결과 확인
- **공유** → **홈 화면에 추가** → 앱처럼 사용

## 4. 참고

- **무료 플랜**: 30초 요청 제한이 있어, 조회에 20~30초 걸릴 수 있음
- **첫 조회**: 서비스가 sleep 상태면 50초 정도 기다릴 수 있음 (무료 플랜 spin-down)
- **결과 캐시**: 한 번 조회한 후 5분간 캐시되므로 재조회 시 빠름
