import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from dotenv import load_dotenv

load_dotenv()

def list_ads():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    try:
        ads = account.get_ads(fields=['id', 'name', 'status', 'effective_status', 'adset_id'])
        if not ads:
            print("이 계정에 생성된 광고(Ad)가 없습니다.")
            return

        print(f"--- 광고(Ad) 목록 ---")
        for ad in ads:
            print(f"Ad Name: {ad['name']} (ID: {ad['id']})")
            print(f" - 상태: {ad['status']} / {ad['effective_status']}")
            print(f" - 소속 광고세트 ID: {ad['adset_id']}")
            print("-" * 20)
    except Exception as e:
        print(f"Error fetching ads: {e}")

if __name__ == "__main__":
    list_ads()
