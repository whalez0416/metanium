import pandas as pd
from monitor_service import MonitorService
from rule_engine import PlaybookRuleEngine
from rule_engine_ab import CampaignABTestEngine

class MockMonitorService(MonitorService):
    def __init__(self):
        super().__init__(interval_minutes=1)
        # Discord 웹후크가 없어도 테스트를 위해 강제 성공으로 시뮬레이션
        self.notifier.webhook_url = "http://mock-webhook-url"

    def check_performance(self):
        print("\n[알림 테스트 시뮬레이션 시작]")
        
        # 1단계: 문제 상황이 포함된 가짜 데이터 생성
        mock_data = [
            {
                'ad_id': 'ad_critical_1',
                'ad_name': 'CPA 폭발 광고 (고위험)',
                'campaign_name': 'Camp_A',
                'spend': 50000,
                'leads': 1,
                'cpa': 50000,
                'ctr': 0.5,
                'created_at': '2026-03-20T00:00:00Z',
                'total_amount_spent': 500000
            },
            {
                'ad_id': 'ad_drain_2',
                'ad_name': '지출 과다 소재 (전환 없음)',
                'campaign_name': 'Camp_A',
                'spend': 35000,
                'leads': 0,
                'cpa': 0,
                'ctr': 1.0,
                'created_at': '2026-03-20T00:00:00Z',
                'total_amount_spent': 500000
            },
            {
                'ad_id': 'ad_safe_3',
                'ad_name': '정상 작동 소재',
                'campaign_name': 'Camp_A',
                'spend': 10000,
                'leads': 1,
                'cpa': 10000,
                'ctr': 1.5,
                'created_at': '2026-03-20T00:00:00Z',
                'total_amount_spent': 500000
            }
        ]
        
        df = pd.DataFrame(mock_data)
        
        # 2단계: Rule Engine & AB Test 통합
        rule_engine = PlaybookRuleEngine()
        ab_engine = CampaignABTestEngine()
        
        df['suggestion'] = df.apply(lambda row: rule_engine.get_action_recommendation(row), axis=1)
        df = ab_engine.analyze_campaigns(df)
        
        print(df[['ad_name', 'suggestion']])

        # 3단계: 알림 탐지 및 발송
        # MonitorService의 탐지 로직 (여기서는 직접 구현)
        alerts_found = []
        for _, row in df.iterrows():
            if "PAUSE" in row['suggestion'] and row['cpa'] > 35000:
                alerts_found.append({
                    'type': 'CRITICAL_CPA',
                    'ad_name': row['ad_name'],
                    'message': f"긴급: CPA가 {row['cpa']:,.0f}원으로 매우 높습니다."
                })
            
            if "PAUSE" in row['suggestion'] and row['leads'] == 0 and row['spend'] > 30000:
                alerts_found.append({
                    'type': 'NO_LEAD_SPEND',
                    'ad_name': row['ad_name'],
                    'message': f"경고: {row['spend']:,.0f}원 지출되었으나 전환이 없습니다."
                })

        self.dispatch_alerts(alerts_found)

if __name__ == "__main__":
    test_service = MockMonitorService()
    test_service.check_performance()
    print("\n[알림 테스트 완료]")
