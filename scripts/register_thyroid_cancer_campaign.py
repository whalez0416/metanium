import json
import os
import sys
from datetime import datetime

# core 폴더를 path에 추가하여 campaign_manager를 임포트할 수 있게 함
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from campaign_manager import MetaCampaignManager

def register_effective_thyroid_campaign(dry_run=True):
    manager = MetaCampaignManager(dry_run=dry_run)
    today_str = datetime.now().strftime('%Y-%m-%d')
    page_id = "102707905966427" # 외과의사 김종민 페이지 ID

    print(f"--- [메타니움] 고효율 갑상선 암캠페인 (A/B Test) 등록 시작 ---\n")
    
    # [전략] 성과 극대화를 위한 A/B 테스트 구조
    # 캠페인명에 '전략' 명시
    campaign_name = f"[{today_str}] 갑상선암_고효율_리드수집_AB테스트"
    campaign_id = manager.find_campaign_by_name(campaign_name)
    if not campaign_id:
        campaign_id = manager.create_campaign(name=campaign_name, objective='OUTCOME_LEADS')

    # --- 전략 A: 공감 및 안심 (Human-Centric) ---
    adset_a_name = "전략A_공감형_3055여성_안심검진"
    targeting_a = {
        'geo_locations': {'countries': ['KR'], 'location_types': ['home']},
        'age_min': 30, 'age_max': 55, 'genders': [2], # 여성 타겟
        'targeting_automation': {'advantage_audience': 1}
    }
    adset_a_id = manager.create_ad_set(
        campaign_id=campaign_id,
        name=adset_a_name,
        daily_budget=3000000, # 30,000원
        targeting=targeting_a,
        page_id=page_id
    )

    image_a = "thyroid_human.png"
    if os.path.exists(image_a) or dry_run:
        hash_a = manager.upload_image(image_a) if os.path.exists(image_a) else "HASH_A"
        creative_a_id = manager.create_ad_creative(
            name=f"소재A_공감_전문의상담_{today_str}",
            image_hash=hash_a,
            headline="혹시 목에 이물감이 느껴지시나요?",
            body="혼자 고민하지 마세요. 여성 전문의의 따뜻하고 세밀한 진료로 갑상선 건강을 확인해 드립니다. 지금 바로 상담 신청하세요.",
            page_id=page_id
        )
        manager.create_ad(ad_set_id=adset_a_id, creative_id=creative_a_id, name="광고A_공감형_이미지")

    # --- 전략 B: 전문성 및 기술 (Tech-Centric) ---
    adset_b_name = "전략B_기술형_3065전체_정밀진단"
    targeting_b = {
        'geo_locations': {'countries': ['KR'], 'location_types': ['home']},
        'age_min': 30, 'age_max': 65, 'genders': [1, 2], # 전체 타겟
        'targeting_automation': {'advantage_audience': 1}
    }
    adset_b_id = manager.create_ad_set(
        campaign_id=campaign_id,
        name=adset_b_name,
        daily_budget=3000000,
        targeting=targeting_b,
        page_id=page_id
    )

    image_b = "thyroid_tech.png"
    if os.path.exists(image_b) or dry_run:
        hash_b = manager.upload_image(image_b) if os.path.exists(image_b) else "HASH_B"
        creative_b_id = manager.create_ad_creative(
            name=f"소재B_기술_정밀장비_{today_str}",
            image_hash=hash_b,
            headline="0.1mm의 오차도 없는 갑상선 정밀 검사",
            body="대학병원급 최첨단 초음파 장비와 암 진단 시스템. 정확한 결과가 건강한 미래를 만듭니다. 암센터 수준의 진단을 경험하세요.",
            page_id=page_id
        )
        manager.create_ad(ad_set_id=adset_b_id, creative_id=creative_b_id, name="광고B_기술형_이미지")

    print(f"\n--- 고효율 캠페인 구성 완료 (2개 세트, 2개 광고) ---")
    update_configs(campaign_name)

def update_configs(campaign_name):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'campaign_configs.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except:
        configs = {}

    configs[campaign_name] = {
        "target_cpa": 18000, # 효율을 위해 CPA 목표를 조금 더 타이트하게 설정
        "protect_hours": 72,
        "max_daily_budget": 300000,
        "auto_pilot": True,
        "ab_test_mode": True # 메타니움 룰 엔진에 AB 테스트 중임을 알림
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)
    print(f"'{campaign_name}'의 고효율 운영 설정이 저장되었습니다.")

if __name__ == "__main__":
    register_effective_thyroid_campaign(dry_run=False)
