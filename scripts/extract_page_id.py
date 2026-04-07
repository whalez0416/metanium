import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from dotenv import load_dotenv

load_dotenv()

def extract_real_page_id():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    print(f"--- 광고 계정({ad_account_id})에서 페이지 ID 추출 시도 ---")
    try:
        # 최근 광고 소재 5개를 조회하여 페이지 ID를 찾음
        creatives = account.get_ad_creatives(fields=['actor_id', 'object_story_spec', 'object_id'])
        
        found_ids = set()
        for creative in creatives:
            # object_story_spec 내에 page_id가 포함된 경우가 많음
            spec = creative.get('object_story_spec')
            if spec and 'page_id' in spec:
                found_ids.add(spec['page_id'])
            
            # actor_id가 페이지 ID인 경우도 있음
            actor_id = creative.get('actor_id')
            if actor_id:
                found_ids.add(actor_id)

        if found_ids:
            print(f"\n검출된 페이지 ID 목록: {list(found_ids)}")
        else:
            print("\n기존 광고 소재에서 페이지 ID를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"Error extracting page_id: {e}")

if __name__ == "__main__":
    extract_real_page_id()
