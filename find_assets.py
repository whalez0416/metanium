import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User
from facebook_business.adobjects.adaccount import AdAccount
from dotenv import load_dotenv

load_dotenv()

def find_my_assets():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    
    print("--- [1] 접근 가능한 페이지(Pages) 목록 조회 ---")
    try:
        me = User(fbid='me')
        pages = me.get_accounts(fields=['id', 'name', 'access_token'])
        for page in pages:
            print(f"Page Name: {page['name']}, ID: {page['id']}")
    except Exception as e:
        print(f"User Pages error: {e}")

    print("\n--- [2] 광고 계정 연관 페이지(Promoted Pages) 조회 ---")
    try:
        account = AdAccount(ad_account_id)
        pages = account.get_promote_pages(fields=['id', 'name'])
        for page in pages:
            print(f"Promoted Page: {page['name']}, ID: {page['id']}")
    except Exception as e:
        print(f"AdAccount Promoted Pages error: {e}")

if __name__ == "__main__":
    find_my_assets()
