import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

load_dotenv()

def list_campaigns():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    if not access_token or not ad_account_id:
        print("Error: FACEBOOK_ACCESS_TOKEN or FACEBOOK_AD_ACCOUNT_ID not found in .env")
        return

    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    print(f"--- Meta Ads 캠페인 목록 (계정: {ad_account_id}) ---")
    
    fields = ['id', 'name', 'status', 'objective', 'effective_status', 'created_time']
    campaigns = account.get_campaigns(fields=fields)

    if not campaigns:
        print("등록된 캠페인이 없습니다.")
        return

    for camp in campaigns:
        print(f"\n[캠페인] {camp['name']} (ID: {camp['id']})")
        print(f" - 상태: {camp['status']} / {camp['effective_status']}")
        print(f" - 목표: {camp['objective']}")
        print(f" - 생성일: {camp['created_time']}")

        # 해당 캠페인의 광고 세트도 확인
        ad_sets = camp.get_ad_sets(fields=['id', 'name', 'status'])
        for ad_set in ad_sets:
            print(f"   ㄴ [광고 세트] {ad_set['name']} (ID: {ad_set['id']}, 상태: {ad_set['status']})")
            
            # 해당 광고 세트의 광고도 확인
            ads = ad_set.get_ads(fields=['id', 'name', 'status'])
            for ad in ads:
                print(f"      ㄴ [광고] {ad['name']} (ID: {ad['id']}, 상태: {ad['status']})")

if __name__ == "__main__":
    list_campaigns()
