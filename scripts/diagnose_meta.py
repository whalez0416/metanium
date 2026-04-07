import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_meta_status():
    token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
    page_id = "1023710997494714" # Min Hospital thyroid center page ID from register_min_hospital_campaign.py

    print(f"--- Meta API Diagnostic ---")
    print(f"Ad Account: {ad_account_id}")
    print(f"Page ID: {page_id}")

    # 1. Check Token Permissions and Scopes
    debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
    try:
        response = requests.get(debug_url).json()
        data = response.get('data', {})
        scopes = data.get('scopes', [])
        print(f"\n[Token Scopes]:")
        for scope in scopes:
            print(f" - {scope}")
        
        expires_at = data.get('data_access_expires_at')
        if expires_at:
            from datetime import datetime
            dt_object = datetime.fromtimestamp(expires_at)
            print(f"Data Access Expires At: {dt_object}")

    except Exception as e:
        print(f"Error checking token: {e}")

    # 2. Check Lead Ads TOS status for the page
    tos_url = f"https://graph.facebook.com/v19.0/{page_id}/leadgen_tos_accepted"
    params = {'access_token': token}
    try:
        response = requests.get(tos_url, params=params).json()
        print(f"\n[Lead Ads TOS Status]:")
        print(response)
    except Exception as e:
        print(f"Error checking TOS: {e}")

    # 3. Check Page Info
    page_url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {'fields': 'name,access_token,category', 'access_token': token}
    try:
        response = requests.get(page_url, params=params).json()
        print(f"\n[Page Info]:")
        print(response)
    except Exception as e:
        print(f"Error checking page: {e}")

if __name__ == "__main__":
    check_meta_status()
