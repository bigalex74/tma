import requests
import time
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TMA-Polling-Raw")

BOT_TOKEN = "8591497428:AAEbVnPaXYe2E-WI2ni2cCuSGnmgS5sckR0"
N8N_WEBHOOK = "https://bigalexn8n.ru/webhook/trigger-translation"
PROXY = {"https": "http://127.0.0.1:10808"}
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def run_polling():
    offset = 0
    logger.info("Raw polling bot started...")
    
    while True:
        try:
            # Запрос обновлений напрямую
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=60"
            resp = requests.get(url, proxies=PROXY, timeout=70)
            data = resp.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if message:
                        logger.info(f"Received msg ID: {message.get('message_id')}")
                        # Отправка в n8n
                        requests.post(N8N_WEBHOOK, json={"message": message}, timeout=15)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_polling()
EOF
# Обновляем CMD для запуска нового скрипта
sed -i 's|telegram_polling.py|telegram_polling.py|g' /home/user/telegram-apps/Dockerfile
docker compose -f /home/user/lightrag/docker-compose.yml up -d --build apps-hub
