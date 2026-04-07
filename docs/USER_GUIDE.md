# 메타니움(Metanium) 사용 설명서

메타니움 광고 운영 자동화 도구를 설치하고 실행하는 단계별 가이드입니다. 프로젝트 구조가 대폭 개선되어 더욱 체계적인 운영이 가능해졌습니다.

---

## 1. 프로젝트 구조 (Hierarchy)

- **`core/`**: 시스템의 두뇌 (Rule Engine, Campaign Manager 등 최상위 로직)
- **`services/`**: 24시간 상시 가동되는 핵심 서비스 (Monitoring, Execution)
- **`scripts/`**: 캠페인 등록, 성과 수집, 진단 등 실행용 도구들
- **`data/`**: 각종 설정 파일(`json`), 의사결정 이력, 플레이북 텍스트
- **`logs/`**: 광고 설정 및 시스템 운영 상세 로그
- **`docs/`**: 기능 명세 및 사용자 가이드

---

## 2. 초기 설치 및 환경 설정 (Setup)

### 2-1. 필수 라이브러리 설치
프로젝트 루트 폴더에서 아래 명령어를 실행합니다.
```bash
pip install -r requirements.txt
```

### 2-2. API 인증 정보 설정 (.env)
루트 폴더의 `.env` 파일을 열어 메타 광고 계정 정보를 입력합니다.
- `FACEBOOK_ACCESS_TOKEN`: 메타 비즈니스 설정에서 발급받은 **영구 토큰**
- `FACEBOOK_AD_ACCOUNT_ID`: 광고 계정 ID (예: `act_123456789`)
- `DISCORD_WEBHOOK_URL`: 알림을 받을 디스코드 웹후크 URL

---

## 3. 주요 기능 실행 방법 (Running)

모든 실행 스크립트는 **`scripts/`** 또는 **`services/`** 폴더에 위치합니다.

### 3-1. 실시간 성과 분석 (One-time Fetch)
현재 계정의 광고 성과를 즉시 수집하고 AI 제안을 확인합니다.
```bash
python scripts/fetch_performance.py
```

### 3-2. 상시 모니터링 및 자동화 (Always-on Service)
24시간 광고를 감시하고 설정된 룰에 따라 자동 조치(Auto-Pilot)를 수행합니다.
```bash
python services/monitor_service.py
```

### 3-3. 캠페인 및 광고 목록 확인
```bash
python scripts/list_campaigns.py  # 캠페인 및 광고세트 목록
python scripts/list_ads.py        # 상세 광고(소재) 목록
```

---

## 4. 운영 로그 및 이력 확인 (Logs & History)

메타니움은 모든 활동을 기록하여 투명한 운영을 지원합니다.

1.  **광고 설정 로그 (`logs/ad_setting_log.json`)**:
    - 캠페인 생성, 예산 변경 등 주요 설정 변경 이력이 기록됩니다.
2.  **의사결정 이력 (`data/decision_history.json`)**:
    - AI가 제안한 모든 조치(PAUSE, SCALE UP 등)의 이유와 상태가 기록됩니다.
3.  **캠페인 개별 설정 (`data/campaign_configs.json`)**:
    - 캠페인별 Target CPA, 보호 기간 등을 여기서 관리합니다.

---

## 5. 운영 전략 수정 (Strategy)

- **글로벌 전략**: `core/rule_engine.py`에서 기본 CPA 및 로직 수정.
- **캠페인 전략**: `data/campaign_configs.json`에서 캠페인별 맞춤 수치 설정.
- **마케팅 플레이북**: `data/marketer_playbook.txt`에 운영 원칙을 텍스트로 정리.
