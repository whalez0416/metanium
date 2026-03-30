import time
import datetime
import pandas as pd
from fetch_performance import fetch_meta_performance
from notifier import DiscordNotifier
from rule_engine_ab import CampaignABTestEngine

class MonitorService:
    def __init__(self, interval_minutes=60):
        self.interval_seconds = interval_minutes * 60
        self.notifier = DiscordNotifier()
        self.last_alerts = {} # {(ad_id, alert_type): timestamp}

    def run(self):
        print(f"[{datetime.datetime.now()}] Metanium 상시 모니터링 서비스를 시작합니다. (주기: {self.interval_seconds//60}분)")
        self.notifier.send_message("Metanium 모니터링 서비스가 시작되었습니다.", title="서비스 시작", color=0x00FF00)

        while True:
            try:
                self.check_performance()
            except Exception as e:
                print(f"모니터링 중 오류 발생: {e}")
                self.notifier.send_message(f"시스템 오류 발생: {e}", title="시스템 장애 알림", color=0xFF0000)
            
            print(f"[{datetime.datetime.now()}] 다음 확인까지 대기합니다...")
            time.sleep(self.interval_seconds)

    def check_performance(self):
        print(f"[{datetime.datetime.now()}] 광고 성과 데이터를 수집 중...")
        df = fetch_meta_performance()

        if df is None or df.empty:
            print("수집된 데이터가 없습니다.")
            return

        # 문제 상황 탐지 로직
        alerts_found = []
        
        for _, row in df.iterrows():
            # 1. 고CPA 알림 (타겟의 1.8배 초과시 긴급 알림)
            # (rule_engine에서 PAUSE를 제안하지만, 실시간 알림은 더 높은 기준 적용 가능)
            if "PAUSE" in row['suggestion'] and row['cpa'] > 35000: # 예시: 3.5만원 초과시
                alerts_found.append({
                    'type': 'CRITICAL_CPA',
                    'ad_name': row['ad_name'],
                    'message': f"긴급: CPA가 {row['cpa']:,.0f}원으로 매우 높습니다. 즉시 확인이 필요합니다."
                })

            # 2. 지출 과다 알림 (전환 없이 지출만 많을 때)
            if "전환 없음" in row['suggestion'] and row['spend'] > 30000:
                alerts_found.append({
                    'type': 'NO_LEAD_SPEND',
                    'ad_name': row['ad_name'],
                    'message': f"경고: {row['spend']:,.0f}원 지출되었으나 전환이 없습니다."
                })

        # 알림 발송 및 중복 방지
        self.dispatch_alerts(alerts_found)

    def dispatch_alerts(self, alerts):
        now = datetime.datetime.now()
        for alert in alerts:
            alert_key = (alert['ad_name'], alert['type'])
            
            # 동일 알림은 24시간 내 1회만 발송 (알림 피로도 방지)
            last_time = self.last_alerts.get(alert_key)
            if isinstance(last_time, datetime.datetime):
                if (now - last_time).total_seconds() < 86400:
                    continue

            # 알림 발송
            success = self.notifier.send_message(
                content=f"**광고명:** {alert['ad_name']}\n**내용:** {alert['message']}",
                title=f"Metanium 경고: {alert['type']}",
                color=0xFF0000
            )
            
            if success:
                self.last_alerts[alert_key] = now
                print(f"알림 발송 완료: {alert['type']} - {alert['ad_name']}")

if __name__ == "__main__":
    # 테스트를 위해 10초 주기로 실행 (실제 운영은 60분 추천)
    service = MonitorService(interval_minutes=60)
    service.run()
