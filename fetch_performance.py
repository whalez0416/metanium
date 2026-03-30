import os
import pandas as pd
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights

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
    ]

    # 3. 파라미터 구성 (오늘 성과 기준)
    params = {
        'date_preset': 'today',
        'level': 'ad',  # 소재(Ad) 단위로 수집
    }

    try:
        # 4. 데이터 조회 (Insights API)
        insights = account.get_insights(fields=fields, params=params)
        
        data = []
        for entry in insights:
            # 기본 데이터 추출
            row = {
                'account_name': entry.get('account_name'),
                'campaign_name': entry.get('campaign_name'),
                'adset_name': entry.get('adset_name'),
                'ad_name': entry.get('ad_name'),
                'spend': float(entry.get('spend', 0)),
                'impressions': int(entry.get('impressions', 0)),
                'clicks': int(entry.get('clicks', 0)),
            }

            # 리드(Lead) 수 추출 (actions 리스트에서 'lead' 또는 'on_facebook_leads' 필터링)
            leads = 0
            actions = entry.get('actions', [])
            for action in actions:
                # 병원 광고의 경우 주로 'lead' 혹은 'offsite_conversion.fb_pixel_lead' 등을 사용
                if action.get('action_type') == 'lead' or action.get('action_type') == 'on_facebook_leads':
                    leads += int(action.get('value', 0))
            
            row['leads'] = leads

            # 5. 파생 지표 계산
            # CPA (Cost Per Action)
            row['cpa'] = row['spend'] / row['leads'] if row['leads'] > 0 else 0
            
            # CTR (Click Through Rate)
            row['ctr'] = (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0

            data.append(row)

        # 6. Pandas DataFrame 생성 및 정리
        df = pd.DataFrame(data)
        
        if not df.empty:
            # 보기 편하게 컬럼 순서 조정
            column_order = [
                'campaign_name', 'adset_name', 'ad_name', 
                'spend', 'leads', 'cpa', 'ctr'
            ]
            df = df[column_order]
            
            # 숫자 데이터 포맷팅 (소수점 2자리)
            df['spend'] = df['spend'].round(0)
            df['cpa'] = df['cpa'].round(0)
            df['ctr'] = df['ctr'].round(2)

        return df

    except Exception as e:
        print(f"Meta API 호출 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    print("메타 광고 성과 데이터를 수집 중입니다 (오늘 기준)...")
    performance_df = fetch_meta_performance()
    
    if performance_df is not None:
        if performance_df.empty:
            print("조회된 광고 성과 데이터가 없습니다.")
        else:
            print("\n--- 오늘의 광고 성과 요약 ---")
            print(performance_df.to_string(index=False))
            
            # CSV로 임시 저장 (로그용)
            # performance_df.to_csv('daily_performance_log.csv', index=False)
            # print("\n'daily_performance_log.csv' 파일로 저장되었습니다.")
