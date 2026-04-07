import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights

# 프로젝트 루트를 path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.rule_engine import PlaybookRuleEngine

load_dotenv()

def monitor_account(date_preset='today'):
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    fields = [
        AdsInsights.Field.campaign_name,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.ad_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks,
        AdsInsights.Field.actions,
        AdsInsights.Field.ad_id,
    ]

    params = {
        'date_preset': date_preset,
        'level': 'ad',
    }

    try:
        insights = account.get_insights(fields=fields, params=params)
        data = []
        rule_engine = PlaybookRuleEngine()

        for entry in insights:
            row = {
                'campaign_name': entry.get('campaign_name'),
                'adset_name': entry.get('adset_name'),
                'ad_name': entry.get('ad_name'),
                'spend': float(entry.get('spend', 0)),
                'impressions': int(entry.get('impressions', 0)),
                'clicks': int(entry.get('clicks', 0)),
            }

            # Leads
            leads = 0
            actions = entry.get('actions', [])
            for action in actions:
                if action.get('action_type') in ['lead', 'on_facebook_leads']:
                    leads += int(action.get('value', 0))
            row['leads'] = leads
            
            # CPA/CTR
            row['cpa'] = row['spend'] / row['leads'] if row['leads'] > 0 else 0
            row['ctr'] = (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0
            
            # Suggestion (using mock fields to avoid error since we didn't fetch ad details here)
            # We just want a quick overview now.
            row['suggestion'] = rule_engine.get_action_recommendation(row)
            data.append(row)

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("--- 실시간 계정 모니터링 (오늘) ---")
    df_today = monitor_account('today')
    if df_today is not None and not df_today.empty:
        print(df_today[['campaign_name', 'ad_name', 'spend', 'leads', 'cpa', 'suggestion']].to_string(index=False))
    else:
        print("오늘 지출 데이터가 아직 없습니다. 전체 기간(Maximum) 성과를 확인합니다...")
        df_maximum = monitor_account('maximum')
        if df_maximum is not None and not df_maximum.empty:
            print(df_maximum[['campaign_name', 'ad_name', 'spend', 'leads', 'cpa', 'suggestion']].to_string(index=False))
        else:
            print("전체 기간(Maximum) 데이터도 조회되지 않습니다. 캠페인이 비활성 상태이거나 설정 오류일 수 있습니다.")
