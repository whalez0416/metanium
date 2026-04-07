import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adimage import AdImage
from dotenv import load_dotenv

load_dotenv()

class MetaCampaignManager:
    def __init__(self, dry_run=True):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.dry_run = dry_run

        if not self.dry_run:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.account = AdAccount(self.ad_account_id)
        else:
            print("[DRY RUN MODE] 실제 API를 호출하지 않고 시뮬레이션합니다.")

    def create_campaign(self, name, objective='OUTCOME_LEADS'):
        """캠페인을 생성합니다."""
        if self.dry_run:
            print(f"[DRY RUN] 캠페인 생성: {name} (목표: {objective})")
            return "mock_campaign_id"

        params = {
            'name': name,
            'objective': objective,
            'status': Campaign.Status.paused, # 일단 멈춘 상태로 생성
            'special_ad_categories': [],
            'is_adset_budget_sharing_enabled': False, # 신규 필수 파라미터 대응
        }
        campaign = self.account.create_campaign(params=params)
        print(f"캠페인 생성 완료: {campaign['id']}")
        return campaign['id']

    def create_ad_set(self, campaign_id, name, daily_budget, targeting, page_id, optimization_goal='LEAD_GENERATION', destination_type='ON_AD'):
        """광고 세트를 생성합니다."""
        if self.dry_run:
            print(f"[DRY RUN] 광고 세트 생성: {name} (예산: {daily_budget}, 페이지: {page_id})")
            return "mock_adset_id"

        params = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget,
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': optimization_goal,
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'targeting': targeting,
            'status': AdSet.Status.paused,
        }

        if optimization_goal == 'LEAD_GENERATION':
            params['promoted_object'] = {'page_id': page_id}
            params['destination_type'] = destination_type
        
        ad_set = self.account.create_ad_set(params=params)
        print(f"광고 세트 생성 완료: {ad_set['id']}")
        return ad_set['id']

    def upload_image(self, image_path):
        """광고 이미지를 업로드합니다."""
        if self.dry_run:
            print(f"[DRY RUN] 이미지 업로드: {image_path}")
            return "mock_image_hash"

        image = AdImage(parent_id=self.ad_account_id)
        image[AdImage.Field.filename] = image_path
        image.remote_create()
        print(f"이미지 업로드 완료: {image[AdImage.Field.hash]}")
        return image[AdImage.Field.hash]

    def create_ad_creative(self, name, image_hash, headline, body, page_id):
        """광고 소재를 생성합니다."""
        if self.dry_run:
            print(f"[DRY RUN] 광고 소재 생성: {name}")
            return "mock_creative_id"

        # 기본적인 단일 이미지 광고 소재 설정
        object_story_spec = {
            'page_id': page_id,
            'link_data': {
                'image_hash': image_hash,
                'link': f"https://www.facebook.com/{page_id}", # 혹은 리드폼 링크
                'message': body,
                'call_to_action': {'type': 'SIGN_UP'},
                'name': headline,
            }
        }

        params = {
            'name': name,
            'object_story_spec': object_story_spec,
        }
        creative = self.account.create_ad_creative(params=params)
        print(f"광고 소재 생성 완료: {creative['id']}")
        return creative['id']

    def create_ad(self, ad_set_id, creative_id, name):
        """최종 광고를 생성합니다."""
        if self.dry_run:
            print(f"[DRY RUN] 광고 생성: {name}")
            return "mock_ad_id"

        params = {
            'name': name,
            'adset_id': ad_set_id,
            'creative': {'creative_id': creative_id},
            'status': Ad.Status.paused,
        }
        ad = self.account.create_ad(params=params)
        print(f"광고 생성 완료: {ad['id']}")
        return ad['id']

    def find_campaign_by_name(self, name):
        """이름으로 기존 캠페인을 찾습니다."""
        if self.dry_run:
            return None
        
        campaigns = self.account.get_campaigns(fields=['id', 'name'], params={'filtering': [{'field': 'name', 'operator': 'EQUAL', 'value': name}]})
        for campaign in campaigns:
            if campaign['name'] == name:
                return campaign['id']
        return None

    def find_ad_set_by_name(self, campaign_id, name):
        """이름으로 기존 광고 세트를 찾습니다."""
        if self.dry_run:
            return None

        campaign = Campaign(campaign_id)
        ad_sets = campaign.get_ad_sets(fields=['id', 'name'], params={'filtering': [{'field': 'name', 'operator': 'EQUAL', 'value': name}]})
        for ad_set in ad_sets:
            if ad_set['name'] == name:
                return ad_set['id']
        return None
