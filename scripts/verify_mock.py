import datetime
import pandas as pd
from rule_engine import PlaybookRuleEngine
from fetch_performance import log_suggestions

def run_mock_verification():
    print("--- 시스템 흐름 검증 (Mock Data) 시작 ---")
    
    engine = PlaybookRuleEngine()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    # Mock 데이터 생성
    mock_data = [
        {
            'ad_id': 'ad_new_123',
            'ad_name': '신규 광고 (24시간 경과)',
            'campaign_name': 'Campaign A',
            'adset_name': 'AdSet A',
            'spend': 10000,
            'leads': 0,
            'cpa': 0,
            'ctr': 1.2,
            'created_at': (now_utc - datetime.timedelta(hours=24)).isoformat(),
            'total_amount_spent': 10000
        },
        {
            'ad_id': 'ad_high_cpa_456',
            'ad_name': '고CPA 광고 (중단 필요)',
            'campaign_name': 'Campaign B',
            'adset_name': 'AdSet B',
            'spend': 50000,
            'leads': 1,
            'cpa': 50000, # Target (20,000) 대비 2.5배
            'ctr': 0.8,
            'created_at': (now_utc - datetime.timedelta(days=10)).isoformat(),
            'total_amount_spent': 500000
        },
        {
            'ad_id': 'ad_good_789',
            'ad_name': '효율 좋은 광고 (증액 필요)',
            'campaign_name': 'Campaign C',
            'adset_name': 'AdSet C',
            'spend': 30000,
            'leads': 3,
            'cpa': 10000, # Target 대비 0.5배
            'ctr': 2.5,
            'created_at': (now_utc - datetime.timedelta(days=15)).isoformat(),
            'total_amount_spent': 450000
        },
        {
            'ad_id': 'ad_ab_winner',
            'ad_name': 'A/B 테스트 승리 소재',
            'campaign_name': 'Campaign_AB',
            'adset_name': 'AdSet_1',
            'spend': 40000,
            'leads': 4,
            'cpa': 10000,
            'ctr': 2.0,
            'created_at': (now_utc - datetime.timedelta(days=5)).isoformat(),
            'total_amount_spent': 200000
        },
        {
            'ad_id': 'ad_ab_loser',
            'ad_name': 'A/B 테스트 패배 소재 (CPA 높음)',
            'campaign_name': 'Campaign_AB',
            'adset_name': 'AdSet_2',
            'spend': 40000,
            'leads': 1,
            'cpa': 40000,
            'ctr': 0.5,
            'created_at': (now_utc - datetime.timedelta(days=5)).isoformat(),
            'total_amount_spent': 200000
        }
    ]
    
    df = pd.DataFrame(mock_data)
    
    # 1. Rule Engine 평가 (기본 룰)
    df['suggestion'] = df.apply(lambda row: engine.get_action_recommendation(row), axis=1)
    
    # 2. A/B 테스트 분석 통합
    from rule_engine_ab import CampaignABTestEngine
    ab_engine = CampaignABTestEngine()
    df = ab_engine.analyze_campaigns(df)

    print("\n[평가 결과 요약 (A/B 테스트 포함)]")
    print(df[['ad_name', 'campaign_name', 'cpa', 'suggestion']])
    
    # 2. 로깅 검증
    print("\n[로깅 실행]")
    log_suggestions(df, log_path='decision_history_mock.json')
    
    # 3. 로그 파일 확인
    import json
    try:
        with open('decision_history_mock.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
            print(f"\n최종 로깅된 제안 수: {len([h for h in history if h['marketer_decision'] == 'PENDING'])}개")
            for entry in history:
                if entry['marketer_decision'] == 'PENDING':
                    print(f"- {entry['ad_name']}: {entry['action_suggested']} ({entry['reason_suggested']})")
    except Exception as e:
        print(f"로그 파일 확인 중 오류: {e}")

if __name__ == "__main__":
    run_mock_verification()
