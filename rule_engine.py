import datetime
import pandas as pd

class PlaybookRuleEngine:
    def __init__(self, playbook_path='marketer_playbook.txt'):
        self.playbook_path = playbook_path
        self.rules = self._load_rules()

    def _load_rules(self):
        """플레이북 파일에서 규칙을 로드합니다. (현재는 단순 저장용)"""
        try:
            with open(self.playbook_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            return []

    def evaluate(self, ad_data):
        """
        광고 성과 데이터를 플레이북 규칙에 따라 평가합니다.
        
        ad_data는 다음 정보를 포함하는 딕셔너리여야 합니다:
        - ad_name, spend, leads, cpa, ctr
        - created_at (Rule 2를 위한 광고 생성 시점)
        - total_amount_spent (Rule 2를 위한 누적 지출액)
        """
        suggestions = []
        is_weekend = datetime.datetime.now().weekday() >= 5 # 5=토, 6=일
        
        # 규칙 1: 주말 CPA 정책
        if is_weekend:
            # 주말에는 CPA가 평일 대비 높게 잡히는 것을 감안합니다.
            pass

        # 규칙 2: 신규 소재 보호 기간 (72시간 또는 50,000원)
        if 'created_at' in ad_data and 'total_amount_spent' in ad_data:
            try:
                # 메타 API는 ISO 포맷의 날짜를 반환합니다.
                created_at = pd.to_datetime(ad_data['created_at'])
                total_spend = float(ad_data['total_amount_spent'])
                
                now = datetime.datetime.now(datetime.timezone.utc)
                # 타임존 보정
                if created_at.tzinfo is None:
                    created_at = created_at.tz_localize('UTC')
                
                hours_since_creation = (now - created_at).total_seconds() / 3600
                
                if hours_since_creation < 72 or total_spend < 50000:
                    suggestions.append({
                        'rule_id': 2,
                        'action': 'KEEP',
                        'reason': f"신규 소재 보호 기간: 생성 후 {hours_since_creation:.1f}시간 경과, 누적 지출 {total_spend:,.0f}원."
                    })
            except Exception as e:
                print(f"규칙 2 평가 중 오류 발생: {e}")

        # 규칙 3: 예산 증액 (최대 20%)
        # get_action_recommendation에서 사용됩니다.
        
        return suggestions

    def get_action_recommendation(self, row):
        """
        성과 지표와 플레이북 규칙을 모두 고려하여 단일 광고에 대한 최적의 조치를 결정합니다.
        """
        # 1. 규칙 2 (신규 소재 보호 기간) 우선 확인
        suggestions = self.evaluate(row)
        for s in suggestions:
            if s['rule_id'] == 2 and s['action'] == 'KEEP':
                return f"KEEP ({s['reason']})"

        # 2. 지표 기반 규칙
        is_weekend = datetime.datetime.now().weekday() >= 5
        # 타겟 CPA (예시: 20,000원)
        target_cpa = 20000
        
        # 주말 CPA 버퍼 (규칙 1: 20-30% 높게 허용)
        effective_target_cpa = target_cpa * 1.3 if is_weekend else target_cpa

        if row['leads'] == 0:
            if row['spend'] > effective_target_cpa:
                return "PAUSE (지출 > 타겟 CPA, 전환 없음)"
            else:
                return "MAINTAIN (데이터 수집 중)"
        
        if row['cpa'] > effective_target_cpa * 1.5:
            return "PAUSE (고CPA > 타겟의 1.5배)"
        elif row['cpa'] < target_cpa * 0.7:
            # 규칙 3: 증액 로직
            return "SCALE UP (+20% 예산 증액 - 규칙 3 부합)"
        
        return "MAINTAIN"

if __name__ == "__main__":
    # Mock 데이터를 활용한 테스트
    engine = PlaybookRuleEngine()
    # 규칙 2 테스트 (최근 광고)
    mock_row_new = {
        'leads': 0, 
        'spend': 15000, 
        'cpa': 0, 
        'ctr': 1.5, 
        'created_at': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)).isoformat(),
        'total_amount_spent': 15000
    }
    print(f"신규 소재 권장 사항: {engine.get_action_recommendation(mock_row_new)}")
    
    # 주말 정책 테스트
    mock_row_weekend = {
        'leads': 1,
        'spend': 25000,
        'cpa': 25000,
        'ctr': 1.0
    }
    print(f"주말 고CPA 권장 사항: {engine.get_action_recommendation(mock_row_weekend)}")
