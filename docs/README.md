# 메타니움 (Metanium)

메타니움은 메타(Meta) 광고 성과를 자동으로 모니터링하고 데이터를 기반으로 의사결정을 실시간 지원하는 광고 운영 자동화 엔진입니다. 마케터의 운영 노하우를 코드로 구현하여, 24시간 끊김 없는 최적화 작업을 수행합니다.

## ✨ 주요 기능

- **실시간 자동 모니터링**: 24시간 광고 계정을 감시하여 성과를 분석합니다.
- **지능형 의사결정 (Rule Engine)**: CPA 지표, 주말 정책, 신규 소재 보호 등을 고려하여 최적의 조치를 제안합니다.
- **Auto-Pilot**: 설정된 임계값에 따라 광고 중단 및 예산 증액을 자동으로 집행합니다.
- **상세 히스토리 관리**: 모든 광고 설정 변경과 AI의 판단 근거를 로그로 투명하게 관리합니다.

## 📂 프로젝트 구조

```text
metanium/
├── core/         # 시스템 핵심 엔진 (규칙 평가, 광고 관리자 등)
├── services/     # 상시 실행 백그라운드 서비스
├── scripts/      # 캠페인 관리 및 성과 수집 유틸리티
├── data/         # 설정 파일 및 의사결정 이력 (JSON)
├── docs/         # 상세 가이드 및 기능 명세서
└── logs/         # 상세 운영 및 설정 변경 로그
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
pip install -r requirements.txt
cp .env.example .env  # 본인의 API 정보를 입력하세요
```

### 2. 성과 즉시 확인
```bash
python scripts/fetch_performance.py
```

### 3. 상시 모니터링 서비스 시작
```bash
python services/monitor_service.py
```

## 📖 상세 문서
더 자세한 내용은 아래 문서들을 참고해 주세요.
- [사용자 가이드 (USER_GUIDE)](docs/USER_GUIDE.md)
- [기능 명세서 (FEATURES)](docs/FEATURES.md)
- [미래 로드맵 (FUTURE_ROADMAP)](docs/FUTURE_ROADMAP.md)

---
*Developed for Meta Ads Automation & Optimization.*
