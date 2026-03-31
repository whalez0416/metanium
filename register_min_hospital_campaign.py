import json
from campaign_manager import MetaCampaignManager

def register_thyroid_campaign():
    # 1. 매니저 초기화 (실제 등록을 위해 DRY_RUN=False 설정)
    manager = MetaCampaignManager(dry_run=False)

    print("--- [민병원] 갑상선 특화 센터 캠페인 등록 시작 ---\n")
    
    # 2. 캠페인 이름 설정 (형식: [날짜] 목표_캠페인명_특이사항)
    from datetime import datetime
    today_str = datetime.now().strftime('%y%m%d')
    # 2 & 5. 기존 성공한 ID 및 이미지 해시 사용 (복구)
    campaign_name = f"[{today_str}] 리드수집_민병원_갑상선센터_신규"
    campaign_id = "6896299324554"
    creative_id = "1446070096924258"
    page_id = "1023710997494714"
    headline = "갑상선 결절, 혹시 암일까 걱정되나요?"
    body = "대학병원급 장비와 숙련된 전문의의 정밀 진단. 민병원에서 자가진단 후 전문 상담을 받아보세요. 지금 리드를 남기시면 상담원이 전화드립니다."
    
    # 3. 타겟팅 설정
    targeting = {
        'geo_locations': {
            'countries': ['KR'],
            'regions': [{'key': '3804', 'name': 'Seoul'}],
            'location_types': ['home'],
        },
        'age_min': 30,
        'age_max': 60,
        'genders': [2],
        'targeting_automation': {'advantage_audience': 0}
    }

    # 4. 광고 세트 신규 생성 (페이지 정보 포함 필수)
    adset_name = "강북권_3060여성_검진유도_v2"
    adset_id = manager.create_ad_set(
        campaign_id=campaign_id,
        name=adset_name,
        daily_budget=3000000,
        targeting=targeting,
        page_id=page_id
    )
    
    print(f"새로운 광고 세트 생성 완료: {adset_id}")

    # 6. 최종 광고 생성
    ad_id = manager.create_ad(
        ad_set_id=adset_id,
        creative_id=creative_id,
        name="갑상선_결절_걱정_이미지광고"
    )

    print(f"\n--- 캠페인 등록 완료 (상태: PAUSED) ---")
    print(f"Campaign ID: {campaign_id}")
    print(f"AdSet ID: {adset_id}")
    print(f"Ad ID: {ad_id}")

    # 7. Metanium 설정 파일(campaign_configs.json)에 자동 추가
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
    register_thyroid_campaign()
