import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from dotenv import load_dotenv

load_dotenv()

def check_current_token_status():
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    
    FacebookAdsApi.init(app_id, app_secret, access_token)
    
    print("--- [메타니움] 토큰 정보 및 약관 상태 확인 ---")
    try:
        # 1. 토큰의 주체 확인 (User 또는 Page)
        me = User(fbid='me').api_get(fields=['id', 'name'])
        print(f"토큰 주체: {me['name']} (ID: {me['id']})")
        
        # 2. 만약 유저 토큰이라면 연결된 모든 페이지 확인
        try:
            pages = User(fbid='me').get_accounts(fields=['id', 'name', 'leadgen_tos_accepted'])
            for p in pages:
                status = "ACCEPTED" if p.get('leadgen_tos_accepted') else "NOT_ACCEPTED"
                print(f"연결 페이지: {p['name']} (ID: {p['id']}) | 약관 상태: {status}")
        except:
            # 페이지 토큰일 경우 바로 약관 확인
            p = Page(fbid='me').api_get(fields=['id', 'name', 'leadgen_tos_accepted'])
            status = "ACCEPTED" if p.get('leadgen_tos_accepted') else "NOT_ACCEPTED"
            print(f"현재 페이지: {p['name']} (ID: {p['id']}) | 약관 상태: {status}")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_current_token_status()
