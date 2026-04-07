import pandas as pd

class CampaignABTestEngine:
    def __init__(self, cpa_threshold=1.3, min_spend=5000):
        """
        캠페인 내 상대적 성과를 분석하는 엔진.
        - cpa_threshold: 캠페인 평균 대비 몇 배의 CPA를 '패배'로 간주할지 (기본 1.3배)
        - min_spend: 분석에 포함할 최소 지출액 (기본 5,000원)
        """
        self.cpa_threshold = cpa_threshold
        self.min_spend = min_spend

    def analyze_campaigns(self, df):
        """
        데이터프레임을 캠페인별로 그룹화하여 상대적 성과를 분석하고 제안을 추가합니다.
        """
        if df is None or df.empty:
            return df

        # 1. 캠페인별 평균 CPA 계산 (지출이 있는 광고 대상)
        valid_ads = df[(df['spend'] >= self.min_spend) & (df['leads'] > 0)].copy()
        
        if valid_ads.empty:
            return df

        # 캠페인별 평균 CPA 산출
        campaign_stats = valid_ads.groupby('campaign_name')['cpa'].mean().rename('campaign_avg_cpa')
        df = df.merge(campaign_stats, on='campaign_name', how='left')

        # 2. 상대적 성과 평가 로직
        def evaluate_relative_performance(row):
            # 이미 룰 엔진(Rule 2 등)에 의해 KEEP/PAUSE 결정이 난 경우는 유지
            if 'KEEP' in row['suggestion'] or 'PAUSE' in row['suggestion']:
                return row['suggestion']

            avg_cpa = row.get('campaign_avg_cpa')
            if pd.isna(avg_cpa) or avg_cpa == 0:
                return row['suggestion']

            # 상대적 저효율 분석 (패배자 찾기)
            if row['leads'] > 0:
                if row['cpa'] > avg_cpa * self.cpa_threshold:
                    return f"PAUSE (A/B 테스트 패배: 캠페인 평균 대비 CPA {row['cpa']/avg_cpa:.1f}배)"
                elif row['cpa'] < avg_cpa * 0.7:
                    return f"SCALE UP (A/B 테스트 승리: 최고 효율 소재)"
            elif row['spend'] > avg_cpa * 1.5:
                # 전환은 없는데 지출은 캠페인 평균 CPA의 1.5배를 넘었을 때
                return f"PAUSE (A/B 테스트 패배: 전환 없이 지출 과다)"

            return row['suggestion']

        df['suggestion'] = df.apply(evaluate_relative_performance, axis=1)
        
        # 임시 컬럼 삭제
        df = df.drop(columns=['campaign_avg_cpa'])
        
        return df

if __name__ == "__main__":
    # 테스트용 Mock 데이터
    test_data = [
        {'campaign_name': '캠페인_A', 'ad_name': '소재_1', 'spend': 50000, 'leads': 5, 'cpa': 10000, 'suggestion': 'MAINTAIN'},
        {'campaign_name': '캠페인_A', 'ad_name': '소재_2', 'spend': 50000, 'leads': 2, 'cpa': 25000, 'suggestion': 'MAINTAIN'},
        {'campaign_name': '캠페인_A', 'ad_name': '소재_3', 'spend': 20000, 'leads': 0, 'cpa': 0, 'suggestion': 'MAINTAIN'}
    ]
    df_test = pd.DataFrame(test_data)
    engine = CampaignABTestEngine()
    result = engine.analyze_campaigns(df_test)
    print(result[['ad_name', 'cpa', 'suggestion']])
