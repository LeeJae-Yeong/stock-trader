"""설정 로드 - .env 환경 변수 사용"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 프로젝트 루트 기준 .env 로드
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def get(key: str, default: str = "") -> str:
    """환경 변수 조회"""
    return os.getenv(key, default)


# 선택적 API 키 (AI 분석 시에만 사용)
OPENAI_API_KEY = get("OPENAI_API_KEY")
