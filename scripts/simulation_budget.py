import pandas as pd
import datetime
from rule_engine import PlaybookRuleEngine
from rule_engine_ab import CampaignABTestEngine

def run_budget_simulation():
    print("="*80)
    print("      Metanium 고예산(3,000,000원) 광고 운영 시뮬레이션")
    print("="*80)
    print("상황: 총 300만원의 예산을 투입하여 2개의 세트와 3개의 소재로 운영 중")
    print("목표: 고지출 환경에서 성과 소재를 식별하고 저효율 소재를 차단하는 AI의 로직 시연\n")

    # 1. 엔진 초기화
    rule_engine = PlaybookRuleEngine(target_cpa=25000) # 타겟 CPA를 2.5만원으로 설정
    ab_engine = CampaignABTestEngine()
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # 2. 고예산 시나리오 데이터 구성 (300만원 지출 상황)
    simulation_data = [
        {
            'ad_name': '메인_소재_01 (Winner)',
            'campaign_name': '300만원_심화_캠페인',
            'adset_name': '관심사_타겟_A',
            'spend': 1500000, 'leads': 150, 'cpa': 10000, 'ctr': 3.2,
            'created_at': (now_utc - datetime.timedelta(days=5)).isoformat(),
            'total_amount_spent': 1500000
        },
        {
            'ad_name': '영상_소재_02 (Keep)',
            'campaign_name': '300만원_심화_캠페인',
            'adset_name': '관심사_타겟_A',
            'spend': 1000000, 'leads': 40, 'cpa': 25000, 'ctr': 1.8,
            'created_at': (now_utc - datetime.timedelta(days=5)).isoformat(),
            'total_amount_spent': 1000000
        },
        {
            'ad_name': '이미지_소재_03 (Loser)',
            'campaign_name': '300만원_심화_캠페인',
            'adset_name': '유사_타겟_B',
            'spend': 500000, 'leads': 10, 'cpa': 50000, 'ctr': 0.7,
            'created_at': (now_utc - datetime.timedelta(days=5)).isoformat(),
            'total_amount_spent': 500000
        }
    ]

    df = pd.DataFrame(simulation_data)

    # 3. 분석 수행
    df['suggestion'] = df.apply(lambda row: rule_engine.get_action_recommendation(row), axis=1)
    df = ab_engine.analyze_campaigns(df)

    # 4. 결과 출력
    pd.set_option('display.max_colwidth', None)
    
    print("-" * 120)
    print(f"{'소재명':<20} | {'세트명':<15} | {'지출액':>10} | {'CPA':>8} | {'CTR':>5}% | {'AI 권장 사항'}")
    print("-" * 120)
    
    total_spend = 0
    for _, row in df.iterrows():
        total_spend += row['spend']
        cpa_str = f"{row['cpa']:,.0f}"
        spend_str = f"{row['spend']:,.0f}"
        print(f"{row['ad_name']:<18} | {row['adset_name']:<14} | {spend_str:>10} | {cpa_str:>8} | {row['ctr']:>6.1f} | {row['suggestion']}")
    
    print("-" * 120)
    print(f"총 지출액 합계: {total_spend:,.0f}원")
    
    print("\n[AI 분석 리포트]")
    print(f"1. 통합 분석: '300만원_심화_캠페인'의 평균 CPA는 {df['cpa'].mean():,.0f}원입니다.")
    print(f"2. 승자 발견: '메인_소재_01'은 타겟 CPA(25,000원) 대비 60% 이상 저렴하며, 캠페인 내 최고 효율을 기록 중입니다. -> [SCALE UP 제안]")
    print(f"3. 패자 차단: '이미지_소재_03'은 타겟 대비 2배 높은 CPA를 보이며 예산을 낭비하고 있습니다. 즉시 중단이 필요합니다. -> [PAUSE 제안]")
    print(f"4. 예산 재배분: 패배 소재에서 아낀 50만원을 승자 소재로 집중 투입하면 기대 리드는 약 50건 추가될 것으로 예측됩니다.")
    print("="*120)

if __name__ == "__main__":
    run_budget_simulation()
