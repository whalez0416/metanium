import sys
import os
import json
from datetime import datetime

# 프로젝트 루트를 path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.campaign_manager import MetaCampaignManager

def register_test_optimization_campaign():
    manager = MetaCampaignManager(dry_run=False) # 실제 등록 모드

    today_str = datetime.now().strftime('%y%m%d')
    campaign_name = f"[TEST] Metanium_AI_Optimization_{today_str}"
    page_id = "1023710997494714" # 민병원 페이지 ID

    print(f"--- [TEST] AI 최적화 운영 테스트 캠페인 생성 시작 ---")

    # 1. 캠페인 생성 (트래픽 목표)
    campaign_id = manager.create_campaign(name=campaign_name, objective='OUTCOME_TRAFFIC')
    
    # 2. 타겟팅 설정 (서울 30-60 여성)
    targeting = {
        'geo_locations': {
            'countries': ['KR'],
            'regions': [{'key': '3804', 'name': 'Seoul'}],
        },
        'age_min': 30,
        'age_max': 60,
        'genders': [2],
        'targeting_automation': {'advantage_audience': 0}
    }

    # 3. 광고 세트 생성 (일일 10,000원)
    adset_name = "AI_Test_Group_01"
    adset_id = manager.create_ad_set(
        campaign_id=campaign_id,
        name=adset_name,
        daily_budget=1000000, # 10,000원 (보통 100배 단위)
        targeting=targeting,
        page_id=page_id,
        optimization_goal='LINK_CLICKS' # 트래픽 목표에 맞게 수정
    )

    # 4. 광고 생성 (기존 소재 활용)
    creative_id = "1446070096924258" # 기존에 확인된 성공 소재 ID
    ad_name = "AI_Test_Ad_01"
    ad_id = manager.create_ad(
        ad_set_id=adset_id,
        creative_id=creative_id,
        name=ad_name
    )

    print(f"\n--- 테스트 캠페인 등록 완료 ---")
    print(f"Campaign ID: {campaign_id}")
    print(f"AdSet ID: {adset_id}")
    print(f"Ad ID: {ad_id}")

    # 5. 전략 설정 업데이트
    update_test_strategy(campaign_name)

def update_test_strategy(campaign_name):
    config_path = 'data/campaign_configs.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except FileNotFoundError:
        configs = {}

    configs[campaign_name] = {
        "target_cpa": 15000,       # 공격적인 CPA 타겟
        "protect_hours": 24,      # 짧은 보호 기간 (빠른 최적화 테스트)
        "max_daily_budget": 50000,
        "auto_pilot": True         # AI 자동 집행 활성화
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)
    print(f"'{campaign_name}'의 AI 운영 전략이 등록되었습니다.")

if __name__ == "__main__":
    register_test_optimization_campaign()
