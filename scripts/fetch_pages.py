import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from dotenv import load_dotenv

load_dotenv()

def get_available_pages():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    FacebookAdsApi.init(app_id, app_secret, access_token)
    account = AdAccount(ad_account_id)

    try:
        pages = account.get_promote_pages(fields=['id', 'name'])
        for page in pages:
            print(f"Page Name: {page['name']}, ID: {page['id']}")
    except Exception as e:
        print(f"Error fetching pages: {e}")

if __name__ == "__main__":
    get_available_pages()
