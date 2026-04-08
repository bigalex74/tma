import telebot
import requests
import json
import time

BOT_TOKEN = "8591497428:AAEbVnPaXYe2E-WI2ni2cCuSGnmgS5sckR0"
N8N_WEBHOOK = "https://bigalexn8n.ru/webhook/21058a05-9f4c-4d4d-b5ad-6cf9ec57412a/webhook"
PROXY = "http://127.0.0.1:10808"

telebot.apihelper.proxy = {'https': PROXY}
bot = telebot.TeleBot(BOT_TOKEN)

print("Polling bot started...")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Отправляем JSON сообщения в n8n
        requests.post(N8N_WEBHOOK, json=json.loads(message.json()), timeout=10)
    except Exception as e:
        print(f"Error forwarding to n8n: {e}")

bot.infinity_polling()
