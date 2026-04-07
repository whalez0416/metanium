import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    def send_message(self, content, title="Metanium Alert", color=0xFF0000):
        """
        메시지를 디스코드 웹후크로 전송합니다.
        """
        if not self.webhook_url:
            # 웹후크가 설정되지 않은 경우 터미널에만 출력
            print(f"[!] Discord Webhook URL이 설정되지 않았습니다. 메일/알림 대신 터미널로 출력합니다.")
            print(f"[{title}] {content}")
            return False

        payload = {
            "embeds": [{
                "title": title,
                "description": content,
                "color": color, # 0xFF0000 = Red
            }]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"디스코드 알림 전송 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    # 테스트 실행
    notifier = DiscordNotifier()
    notifier.send_message("디스코드 알림 모듈이 성공적으로 로드되었습니다.", title="테스트 알림", color=0x00FF00)
