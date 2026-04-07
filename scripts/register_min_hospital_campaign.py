import json
import os
from datetime import datetime
from campaign_manager import MetaCampaignManager

def register_thyroid_campaign(dry_run=True):
    # 1. 매니저 초기화
    manager = MetaCampaignManager(dry_run=dry_run)

    print(f"--- [민병원] 갑상선 특화 센터 캠페인 등록 시작 (DRY_RUN={dry_run}) ---\n")
    
    # 2. 캠페인 설정
    today_str = datetime.now().strftime('%y%m%d')
    campaign_name = f"[{today_str}] 리드수집_민병원_갑상선센터_신규"
    page_id = "1023710997494714"
    
    # 3. 기존 캠페인 확인 또는 생성
    campaign_id = manager.find_campaign_by_name(campaign_name)
    if not campaign_id:
        print(f"새로운 캠페인을 생성합니다: {campaign_name}")
        campaign_id = manager.create_campaign(name=campaign_name, objective='OUTCOME_LEADS')
    else:
        print(f"기존 캠페인을 발견했습니다: {campaign_id}")

    # 4. 타겟팅 설정
    targeting = {
        'geo_locations': {
            'countries': ['KR'],
            'regions': [{'key': '3804', 'name': 'Seoul'}],
            'location_types': ['home'],
        },
        'age_min': 30,
        'age_max': 60,
        'genders': [2], # 여성
        'targeting_automation': {'advantage_audience': 0}
    }

    # 5. 광고 세트 확인 또는 생성
    adset_name = "강북권_3060여성_검진유도_v2"
    adset_id = manager.find_ad_set_by_name(campaign_id, adset_name)
    if not adset_id:
        print(f"새로운 광고 세트를 생성합니다: {adset_name}")
        adset_id = manager.create_ad_set(
            campaign_id=campaign_id,
            name=adset_name,
            daily_budget=3000000, # 30,000원 (API 단위가 다를 수 있음, 보통 100배)
            targeting=targeting,
            page_id=page_id
        )
    else:
        print(f"기존 광고 세트를 발견했습니다: {adset_id}")

    # 6. 광고 소재(Creative) 설정
    # 어제 성공했던 소재 ID를 기본값으로 사용하되, 이미지가 있다면 업로드 로직 추가 가능
    creative_id = "1446070096924258" # 기존 성공 ID (복구용)
    
    # 만약 특정 경로에 이미지가 있다면 업로드 시도 (예시)
    image_path = "thyroid_ad.jpg"
    if os.path.exists(image_path):
        print(f"이미지 발견: {image_path}. 업로드 및 신규 소재 생성을 시도합니다.")
        image_hash = manager.upload_image(image_path)
        creative_id = manager.create_ad_creative(
            name=f"갑상선_결절_신규_소재_{today_str}",
            image_hash=image_hash,
            headline="갑상선 결절, 혹시 암일까 걱정되나요?",
            body="대학병원급 장비와 숙련된 전문의의 정밀 진단. 민병원에서 자가진단 후 전문 상담을 받아보세요.",
            page_id=page_id
        )

    # 7. 광고 생성
    ad_name = "갑상선_결절_걱정_이미지광고"
    ad_id = manager.create_ad(
        ad_set_id=adset_id,
        creative_id=creative_id,
        name=ad_name
    )

    print(f"\n--- 캠페인 등록 절차 완료 ---")
    print(f"Campaign ID: {campaign_id}")
    print(f"AdSet ID: {adset_id}")
    print(f"Ad ID: {ad_id}")

    # 8. Metanium 설정 파일(campaign_configs.json) 업데이트
    update_configs(campaign_name)

def update_configs(campaign_name):
    config_path = 'campaign_configs.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except FileNotFoundError:
        configs = {}

    if campaign_name not in configs:
        configs[campaign_name] = {
            "target_cpa": 15000,
            "protect_hours": 72,
            "max_daily_budget": 100000,
            "auto_pilot": True
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=4, ensure_ascii=False)
        print(f"'{campaign_name}' 정보가 campaign_configs.json에 추가되었습니다.")

if __name__ == "__main__":
    # 사용자의 요청에 따라 실제 등록을 위해 dry_run=False로 실행합니다.
    # 주의: 실제 광고 비용이 발생할 수 있는 캠페인이 생성됩니다.
    register_thyroid_campaign(dry_run=False)
