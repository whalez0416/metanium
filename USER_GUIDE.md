# 메타니움(Metanium) 사용 설명서

메타니움 광고 운영 자동화 도구를 설치하고 실행하는 단계별 가이드입니다.

---

## 1. 초기 설치 및 환경 설정 (Setup)

### 1-1. 필수 라이브러리 설치
프로젝트 폴더 내에서 터미널을 열고 아래 명령어를 입력하여 필요한 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

### 1-2. API 인증 정보 설정 (.env)
1. 프로젝트 루트 폴더에 있는 `.env` 파일을 엽니다.
2. 아래의 항목들에 본인의 메타 광고 계정 정보를 입력합니다.
   - `FACEBOOK_ACCESS_TOKEN`: 메타 개발자 센터에서 발급받은 액세스 토큰
   - `FACEBOOK_AD_ACCOUNT_ID`: 광고 계정 ID (예: `act_123456789`)
   - `FACEBOOK_APP_ID`: 메타 앱 ID
   - `FACEBOOK_APP_SECRET`: 메타 앱 시크릿 코드

---

## 2. 시스템 실행 및 모니터링 (Running)

### 2-1. 실시간 성과 분석 실행
가장 최신의 광고 성과를 바탕으로 AI의 제안을 확인하려면 아래 명령어를 실행합니다.
```bash
python fetch_performance.py
```
- 실행 결과로 터미널에 광고별 성과 요약과 **AI 권장 사항(Suggestion)**이 출력됩니다.

### 2-2. 의사결정 이력 확인
AI가 제안한 `PAUSE`(중단) 또는 `SCALE UP`(증액) 내역은 자동으로 `decision_history.json` 파일에 저장됩니다.
- 이 파일을 열어 AI가 왜 그런 제안을 했는지 상세 이유(reason_suggested)를 확인할 수 있습니다.

---

## 3. 사전 검증 및 데모 실행 (Testing)

### 3-1. 시뮬레이션 데모 실행
실제 광고 데이터 없이 로직이 잘 작동하는지 확인하고 싶을 때 실행합니다.
```bash
python demo.py
```
- 다양한 시나리오(신규 소재, 주말, A/B 테스트 등)에 대해 AI가 어떻게 판단하는지 즉시 확인할 수 있습니다.

---

## 4. 운영 원칙 수정 방법 (Playbook)

광고 운영 정책을 변경하고 싶다면 `marketer_playbook.txt` 파일을 수정하거나, `rule_engine.py` 내의 수치를 조정할 수 있습니다.
- **타겟 CPA 변경**: `rule_engine.py` 파일 내 `target_cpa = 20000` 부분의 숫자를 본인의 업종에 맞게 수정하세요.
- **신규 소재 보호 기간**: `rule_engine.py` 내의 시간(72)이나 지출액(50000) 기준을 변경하여 적용할 수 있습니다.
