import telebot
import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TMA-Polling")

BOT_TOKEN = "8591497428:AAEbVnPaXYe2E-WI2ni2cCuSGnmgS5sckR0"
N8N_WEBHOOK = "http://127.0.0.1:5678/webhook/21058a05-9f4c-4d4d-b5ad-6cf9ec57412a/webhook"
PROXY = "http://127.0.0.1:10808"

telebot.apihelper.proxy = {'https': PROXY}
bot = telebot.TeleBot(BOT_TOKEN)

def run_bot():
    logger.info("Polling bot started...")
    
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        try:
            requests.post(N8N_WEBHOOK, json={"message": json.loads(message.json())}, timeout=15)
        except Exception as e:
            logger.error(f"Forwarding error: {e}")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Polling error: {e}. Restarting in 10s...")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
