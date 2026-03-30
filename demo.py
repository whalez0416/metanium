import pandas as pd
import datetime
from rule_engine import PlaybookRuleEngine
from rule_engine_ab import CampaignABTestEngine

def run_demo():
    print("="*60)
    print("      Metanium AI 광고 운영 엔진 시뮬레이션 데모")
    print("="*60)
    print("설명: 실제 광고 성과 데이터를 모방한 Mock 데이터를 활용하여")
    print("      구현된 모든 운영 원칙과 A/B 테스트 분석 기능을 테스트합니다.\n")

    # 1. 엔진 초기화
    rule_engine = PlaybookRuleEngine()
    ab_engine = CampaignABTestEngine()
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # 2. 시나리오 데이터 구성 (Mock)
    # 각 시나리오별로 어떤 룰이 적용되는지 주석으로 설명
    demo_scenarios = [
        {
            'scenario': '[신규 광고 보호]',
            'ad_name': '신규_GNB_캠페인_1',
            'campaign_name': 'Brand_Search',
            'spend': 12000, 'leads': 0, 'cpa': 0, 'ctr': 1.5,
            'created_at': (now_utc - datetime.timedelta(hours=48)).isoformat(), # 72시간 미만
            'total_amount_spent': 12000
        },
        {
            'scenario': '[주말 성과 허용]',
            'ad_name': '주말_성과_소재_A',
            'campaign_name': 'Conversion_A',
            'spend': 25000, 'leads': 1, 'cpa': 25000, 'ctr': 1.1, # 평일 기준이면 PAUSE 대상
            'created_at': (now_utc - datetime.timedelta(days=10)).isoformat(),
            'total_amount_spent': 350000
        },
        {
            'scenario': '[A/B 테스트 승리]',
            'ad_name': 'AB_캠페인_승리소재',
            'campaign_name': 'AB_Test_Campaign',
            'spend': 40000, 'leads': 4, 'cpa': 10000, 'ctr': 2.2, # 캠페인 내 최고 효율
            'created_at': (now_utc - datetime.timedelta(days=15)).isoformat(),
            'total_amount_spent': 600000
        },
        {
            'scenario': '[A/B 테스트 패배]',
            'ad_name': 'AB_캠페인_패배소재',
            'campaign_name': 'AB_Test_Campaign',
            'spend': 40000, 'leads': 1, 'cpa': 40000, 'ctr': 0.6, # 캠페인 평균 대비 고CPA
            'created_at': (now_utc - datetime.timedelta(days=15)).isoformat(),
            'total_amount_spent': 600000
        },
        {
            'scenario': '[예산 낭비 탐지]',
            'ad_name': 'AB_캠페인_지출과다',
            'campaign_name': 'AB_Test_Campaign',
            'spend': 22000, 'leads': 0, 'cpa': 0, 'ctr': 0.4, # 전환 없이 캠페인 평균 이상 지출
            'created_at': (now_utc - datetime.timedelta(days=15)).isoformat(),
            'total_amount_spent': 400000
        },
        {
            'scenario': '[캠페인 맞춤 타겟]',
            'ad_name': '고단가_제품_광고_1',
            'campaign_name': '구매_고단가_캠페인', # Config상 target_cpa: 45000
            'spend': 40000, 'leads': 1, 'cpa': 40000, 'ctr': 0.8, # 일반 타겟(2만)이면 PAUSE 대상이나, 여기선 MAINTAIN
            'created_at': (now_utc - datetime.timedelta(days=10)).isoformat(),
            'total_amount_spent': 500000
        }
    ]

    df = pd.DataFrame(demo_scenarios)

    # 3. 분석 수행 (개별 룰 -> A/B 테스트 비교)
    df['suggestion'] = df.apply(lambda row: rule_engine.get_action_recommendation(row), axis=1)
    df = ab_engine.analyze_campaigns(df)

    # 4. 결과 출력
    pd.set_option('display.max_colwidth', None)
    
    print("-" * 100)
    print(f"{'시나리오':<18} | {'광고명':<15} | {'CPA':>8} | {'AI 권장 사항'}")
    print("-" * 100)
    
    for _, row in df.iterrows():
        cpa_str = f"{row['cpa']:,.0f}" if row['cpa'] > 0 else "-"
        print(f"{row['scenario']:<14} | {row['ad_name']:<12} | {cpa_str:>8} | {row['suggestion']}")
    
    print("-" * 100)
    print("\n[데모 결과 해석]")
    print("1. [KEEP]: 생성된 지 72시간이 지나지 않은 신규 소재는 성과와 무관하게 보호합니다.")
    print("2. [MAINTAIN]: 주말(토/일)에는 CPA가 소폭 상승해도 즉시 중단하지 않고 지켜봅니다.")
    print("3. [SCALE UP]: 같은 캠페인 안에서 경쟁 광고 대비 효율이 2배 이상 좋으면 증액을 제안합니다.")
    print("4. [PAUSE]: 성과가 극도로 낮거나 캠페인 평균 대비 효율이 나쁜 '패배한 A/B 테스트'는 중단을 제안합니다.")
    print("="*100)

if __name__ == "__main__":
    run_demo()
