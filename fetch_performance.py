import os
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.ad import Ad
from rule_engine import PlaybookRuleEngine
from rule_engine_ab import CampaignABTestEngine
import json

# .env 파일 로드
load_dotenv()

def fetch_meta_performance():
    """
    메타 광고 API를 통해 오늘의 성과 데이터를 가져와 Pandas DataFrame으로 반환합니다.
    """
    # 1. API 인증 정보 설정
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    if not access_token or not ad_account_id:
        print("Error: .env 파일에 FACEBOOK_ACCESS_TOKEN 및 FACEBOOK_AD_ACCOUNT_ID를 설정해주세요.")
        return None

    # API 세션 초기화
    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    # 2. 가져올 필드 정의
    fields = [
        AdsInsights.Field.account_name,
        AdsInsights.Field.campaign_name,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.ad_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks,
        AdsInsights.Field.actions,
        AdsInsights.Field.ad_id,
    ]

    # 3. 파라미터 구성 (오늘 성과 기준)
    params = {
        'date_preset': 'today',
        'level': 'ad',  # 소재(Ad) 단위로 수집
    }

    try:
        # 4. 데이터 조회 (Insights API)
        insights = account.get_insights(fields=fields, params=params)
        
        # 4.1 광고 상태 및 생성일 등 추가 정보 조회 (Rule Engine용)
        # 모든 광고의 기본 정보를 한 번에 가져옴
        ads = account.get_ads(fields=['id', 'name', 'created_time', 'lifetime_spend'])
        ad_details = {ad['id']: ad for ad in ads}

        rule_engine = PlaybookRuleEngine()
        data = []
        for entry in insights:
            ad_id = entry.get('ad_id')
            ad_info = ad_details.get(ad_id, {})

            # 기본 데이터 추출
            row = {
                'ad_id': ad_id,
                'account_name': entry.get('account_name'),
                'campaign_name': entry.get('campaign_name'),
                'adset_name': entry.get('adset_name'),
                'ad_name': entry.get('ad_name'),
                'spend': float(entry.get('spend', 0)),
                'impressions': int(entry.get('impressions', 0)),
                'clicks': int(entry.get('clicks', 0)),
                'created_at': ad_info.get('created_time'),
                'total_amount_spent': ad_info.get('lifetime_spend', 0)
            }

            # 리드(Lead) 수 추출
            leads = 0
            actions = entry.get('actions', [])
            for action in actions:
                if action.get('action_type') in ['lead', 'on_facebook_leads']:
                    leads += int(action.get('value', 0))
            
            row['leads'] = leads

            # 5. 파생 지표 계산
            row['cpa'] = row['spend'] / row['leads'] if row['leads'] > 0 else 0
            row['ctr'] = (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0

            # 6. Rule Engine 평가 및 권장 사항 추가
            row['suggestion'] = rule_engine.get_action_recommendation(row)

            data.append(row)

        # 7. 캠페인별 A/B 테스트 상대적 성과 분석 추가
        df = pd.DataFrame(data)
        if not df.empty:
            ab_engine = CampaignABTestEngine()
            df = ab_engine.analyze_campaigns(df)

        # 8. Pandas DataFrame 생성 및 정리
        if not df.empty:
            # 보기 편하게 컬럼 순서 조정
            column_order = [
                'campaign_name', 'adset_name', 'ad_name', 
                'spend', 'leads', 'cpa', 'ctr', 'suggestion'
            ]
            df = df[column_order]
            
            # 숫자 데이터 포맷팅
            df['spend'] = df['spend'].round(0)
            df['cpa'] = df['cpa'].round(0)
            df['ctr'] = df['ctr'].round(2)

        return df

    except Exception as e:
        print(f"Meta API 호출 중 오류 발생: {e}")
        return None

def log_suggestions(df, log_path='decision_history.json'):
    """
    'PAUSE' 또는 'SCALE UP' 제안을 decision_history.json에 PENDING 상태로 기록합니다.
    """
    if df is None or df.empty:
        return

    # 조치가 필요한 제안만 필터링 (MAINTAIN 또는 KEEP 제외)
    actionable = df[df['suggestion'].str.contains('PAUSE|SCALE UP', regex=True)].copy()
    if actionable.empty:
        return

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_entries = []
    for _, row in actionable.iterrows():
        # 중복 기록 방지 (동일 광고에 대해 같은 날 기록이 있는지 확인)
        already_logged = any(h['ad_id'] == row.get('ad_id', 'N/A') and h['timestamp'][:10] == timestamp[:10] for h in history)
        if not already_logged:
            new_entries.append({
                "timestamp": timestamp,
                "action_suggested": row['suggestion'].split(' ')[0], # 예: "PAUSE"
                "ad_id": row.get('ad_id', 'N/A'),
                "ad_name": row['ad_name'],
                "reason_suggested": row['suggestion'],
                "marketer_decision": "PENDING",
                "marketer_reason": ""
            })

    if new_entries:
        history.extend(new_entries)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"\n{len(new_entries)}건의 새로운 제안이 '{log_path}'에 기록되었습니다.")

if __name__ == "__main__":
    print("메타 광고 성과 데이터를 수집 중입니다 (오늘 기준)...")
    performance_df = fetch_meta_performance()
    
    if performance_df is not None:
        if performance_df.empty:
            print("조회된 광고 성과 데이터가 없습니다.")
        else:
            print("\n--- 오늘의 광고 성과 요약 ---")
            print(performance_df.to_string(index=False))
            
            # 제안 사항 로깅
            log_suggestions(performance_df)
