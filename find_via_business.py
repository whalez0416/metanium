import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.business import Business
from dotenv import load_dotenv

load_dotenv()

def find_pages_via_business():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    
    print("--- [Business] 비즈니스 정보를 통해 페이지 조회 시도 ---")
    try:
        account = AdAccount(ad_account_id)
        # 1. 광고 계정의 비즈니스 정보 조회
        acc_info = account.api_get(fields=['business'])
        business_info = acc_info.get('business')
        
        if not business_info:
            print("이 광고 계정과 연결된 비즈니스 관리자가 없습니다.")
            return

        business_id = business_info['id']
        print(f"발견된 Business ID: {business_id}")

        # 2. 비즈니스 관리자에 소속된 페이지 목록 조회
        biz = Business(business_id)
        pages = biz.get_client_pages(fields=['id', 'name'])
        
        for page in pages:
            print(f"Found Page (Client): {page['name']}, ID: {page['id']}")
            
        owned_pages = biz.get_owned_pages(fields=['id', 'name'])
        for page in owned_pages:
            print(f"Found Page (Owned): {page['name']}, ID: {page['id']}")

    except Exception as e:
        print(f"Error accessing Business Info: {e}")

if __name__ == "__main__":
    find_pages_via_business()
