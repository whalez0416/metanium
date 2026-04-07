import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet

# 프로젝트 루트를 path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# .env 파일 로드 (루트 폴더 기준)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

class MetaExecutionService:
    def __init__(self, dry_run=None):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        
        # 건드리지 않고 로그만 남기는 모드 (기본값은 .env의 DRY_RUN 환경변수 참고)
        if dry_run is None:
            self.dry_run = os.getenv('DRY_RUN', 'True').lower() == 'true'
        else:
            self.dry_run = dry_run

        if not self.dry_run:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)

    def execute_action(self, ad_id, action, campaign_name, configs):
        """
        제안된 조치(PAUSE, SCALE UP)를 실행합니다.
        configs는 campaign_configs.json에서 가져온 해당 캠페인의 설정 딕셔너리입니다.
        """
        auto_pilot = configs.get('auto_pilot', False)
        if not auto_pilot:
            return "SKIPPED (Auto-Pilot Disabled)"

        if "PAUSE" in action:
            return self.pause_ad(ad_id)
        elif "SCALE UP" in action:
            max_budget = configs.get('max_daily_budget', 100000)
            return self.scale_up_ad_set(ad_id, max_budget, percentage=0.2)
        
        return "NO ACTION"

    def pause_ad(self, ad_id):
        """광고를 중단(PAUSE)합니다."""
        if self.dry_run:
            print(f"[DRY RUN] Ad {ad_id} 상태를 PAUSED로 변경 시도")
            return "EXECUTED (DRY RUN)"

        try:
            ad = Ad(ad_id)
            ad.remote_update(fields={'status': Ad.Status.paused})
            print(f"Ad {ad_id} 중단 완료.")
            return "EXECUTED"
        except Exception as e:
            print(f"Ad {ad_id} 중단 중 오류 발생: {e}")
            return f"FAILED ({e})"

    def scale_up_ad_set(self, ad_id, max_budget, percentage=0.2):
        """광고 세트의 예산을 증액합니다 (최대 한도 체크)."""
        try:
            # 1. Ad 정보를 조회하여 부모 AdSet ID와 현재 예산 확인
            if self.dry_run:
                # Dry run 모드에서는 실제 API 호출 대신 가상의 데이터 사용
                ad_set_id = "mock_adset_id"
                current_budget = 50000 # 가상의 현재 예산
            else:
                ad = Ad(ad_id).api_get(fields=['adset_id'])
                ad_set_id = ad['adset_id']
                ad_set = AdSet(ad_set_id).api_get(fields=['daily_budget', 'name'])
                current_budget = float(ad_set.get('daily_budget', 0))

            # 2. 새로운 예산 계산
            new_budget = int(current_budget * (1 + percentage))
            
            # 3. 안전 장치: 최대 예산 한도 체크
            if new_budget > max_budget:
                print(f"증액 중단: 새로운 예산({new_budget:,.0f}원)이 최대 한도({max_budget:,.0f}원)를 초과합니다.")
                return "SKIPPED (Limit Reached)"

            # 4. API 반영
            if self.dry_run:
                print(f"[DRY RUN] AdSet {ad_set_id} 예산을 {current_budget:,.0f} -> {new_budget:,.0f}으로 증액 시도")
                return "EXECUTED (DRY RUN)"
            
            AdSet(ad_set_id).remote_update(fields={'daily_budget': new_budget})
            print(f"AdSet {ad_set_id} 예산 증액 완료: {new_budget:,.0f}원")
            return "EXECUTED"

        except Exception as e:
            print(f"예산 증액 중 오류 발생: {e}")
            return f"FAILED ({e})"

if __name__ == "__main__":
    # 간단한 테스트 실행
    service = MetaExecutionService(dry_run=True)
    res = service.scale_up_ad_set("test_ad_id", max_budget=60000)
    print(f"결과: {res}")
    
    res_limit = service.scale_up_ad_set("test_ad_id", max_budget=40000)
    print(f"한도 초과 테스트 결과: {res_limit}")
