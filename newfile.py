import telebot
import random
import requests
import base64
import json
from datetime import datetime
import time

# Telegram Bot API token'ınızı buraya ekleyin
API_TOKEN = '6981545815:AAHuOOT1uBZRP5dtnuLmQAm17b-7a5r8lF4'
CHANNEL_ID = '@freeinternetv1'  # Kanalınızın kullanıcı adı ya da ID'si
bot = telebot.TeleBot(API_TOKEN)

url = 'https://m.vodafone.com.tr/maltgtwaycbu/api/'

headers = {
    'User-Agent': 'VodafoneMCare/2308211432 CFNetwork/1325.0.1 Darwin/21.1.0',
    'Content-Length': '83',
    'Connection': 'keep-alive',
    'Accept-Language': 'tr_TR',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'm.vodafone.com.tr',
    'Cache-Control': 'no-cache',
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded'
}

def generate_random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def check_subscription(user_id, chat_id):
    chat_member = bot.get_chat_member(chat_id, user_id)
    return chat_member.status in ['member', 'administrator', 'creator']

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_subscription(user_id, CHANNEL_ID):
        bot.reply_to(message, "Merhaba! Lütfen giriş yapmak için /login komutunu kullanın.")
    else:
        bot.reply_to(message, 'Kanalımıza katılmadan işlem yapamazsınız. Lütfen kanala katılın: https://t.me/freeinternetv1')

@bot.message_handler(commands=['login'])
def login(message):
    user_id = message.from_user.id
    if not check_subscription(user_id, CHANNEL_ID):
        bot.reply_to(message, 'Kanalımıza katılmadan işlem yapamazsınız. Lütfen kanala katılın: https://t.me/freeinternetv1')
        return

    msg = bot.reply_to(message, "𝗕𝗔𝗦𝗜𝗡𝗗𝗔 𝗦𝗜𝗙𝗜𝗥 𝗢𝗟𝗠𝗔𝗗𝗔𝗡 𝗧𝗘𝗟𝗘𝗙𝗢𝗡 𝗡𝗨𝗠𝗔𝗥𝗔𝗡𝗜 𝗚𝗜𝗥: ")
    bot.register_next_step_handler(msg, process_telno)

def process_telno(message):
    telno = message.text
    msg = bot.reply_to(message, "7000'𝗘 '𝗦' 𝗚𝗢𝗡𝗗𝗘𝗥 𝗚𝗘𝗟𝗘𝗡 𝗞𝗢𝗗𝗨 𝗕𝗨𝗥𝗔𝗬𝗔 𝗬𝗔𝗭: ")
    bot.register_next_step_handler(msg, lambda m: process_password(m, telno))

def process_password(message, telno):
    parola = message.text

    data = {
        'context': 'e30=',
        'username': telno,
        'method': 'twoFactorAuthentication',
        'password': parola
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        bot.reply_to(message, f'Hata: {response.status_code} - {response.text}')
        return
    
    try:
        response_json = response.json()
        proid = response_json.get('process_id')
    except json.JSONDecodeError:
        bot.reply_to(message, 'Yanıt JSON formatında değil.')
        return

    if proid is None:
        bot.reply_to(message, '𝗞𝗡𝗞 𝗡𝗨𝗠𝗔𝗥𝗔𝗡𝗜𝗗𝗢𝗚𝗥𝗨 𝗚𝗜𝗥𝗗𝗘 𝗖𝗔𝗥𝗞𝗜𝗡𝗜 𝗖𝗘𝗩𝗜𝗥 𝗛𝗔𝗗𝗘 𝗧𝗘𝗞𝗥𝗔𝗥 𝗕𝗔𝗦𝗟𝗔𝗧❌')
        return

    bot.reply_to(message, '𝗛𝗔𝗗𝗘 𝗜𝗬𝗜𝗦𝗜𝗡 𝗚𝗜𝗥𝗜𝗦 𝗕𝗔𝗦𝗔𝗥𝗜𝗟𝗜✅')
    msg = bot.reply_to(message, '[+] 𝗦𝗠𝗦 𝗜𝗟𝗘 𝗚𝗘𝗟𝗘𝗡 𝗞𝗢𝗗𝗨 𝗨𝗡𝗨𝗧𝗠𝗔:')
    bot.register_next_step_handler(msg, lambda m: process_otp(m, proid))

def process_otp(message, proid):
    kod = message.text
    veri = {
        'langId': 'tr_TR',
        'clientVersion': '17.2.5',
        'reportAdvId': '0AD98FF8-C8AB-465C-9235-DDE102D738B3',
        'pbmRight': '1',
        'rememberMe': 'true',
        'sid': proid,
        'otpCode': kod,
        'platformName': 'iPhone'
    }

    base64_veri = base64.b64encode(json.dumps(veri).encode('utf-8')).decode('utf-8')

    data2 = {
        'context': base64_veri,
        'grant_type': 'urn:vodafone:params:oauth:grant-type:two-factor',
        'code': kod,
        'method': 'tokenUsing2FA',
        'process_id': proid,
        'scope': 'ALL'
    }

    response2 = requests.post(url, headers=headers, data=data2)
    if response2.status_code != 200:
        bot.reply_to(message, f'Hata: {response2.status_code} - {response2.text}')
        return
    
    try:
        sonuc2 = response2.json()
    except json.JSONDecodeError:
        bot.reply_to(message, 'Yanıt JSON formatında değil.')
        return

    o_head = {
        'Accept': 'application/json',
        'Language': 'tr',
        'ApplicationType': '1',
        'ClientKey': 'AC491770-B16A-4273-9CE7-CA790F63365E',
        'sid': proid,
        'Content-Type': 'application/json',
        'Content-Length': '54',
        'Host': 'm.vodafone.com.tr',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/4.10.0',
        'X-Forwarded-For': generate_random_ip()
    }

    bot.reply_to(message, '𝗚𝗜𝗥𝗜𝗦 𝗬𝗔𝗣𝗜𝗟𝗗𝗜 ✅')
    time.sleep(3)

    msg = bot.reply_to(message, '𝗛𝗔𝗡𝗚𝗜 𝗜𝗦𝗟𝗘𝗠𝗜 𝗬𝗔𝗣𝗠𝗔𝗞 𝗜𝗦𝗧𝗘𝗗𝗜𝗡 𝗞𝗡𝗞𝗠?\n\n[1] 𝗖𝗔𝗥𝗞𝗜 𝗖𝗘𝗕𝗜𝗥 \n[2] 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗞𝗔𝗡𝗔𝗟𝗜𝗡𝗔 𝗞𝗔𝗧𝗜𝗟')
    bot.register_next_step_handler(msg, lambda m: process_action(m, proid, o_head))

def process_action(message, proid, o_head):
    sec = message.text

    if sec == '1':
        cark_data = {
            'clientKey': 'AC491770-B16A-4273-9CE7-CA790F63365E',
            'clientVersion': '16.8.3',
            'language': 'tr',
            'operatingSystem': 'android'
        }
        cark_url = f'https://m.vodafone.com.tr/squat/getSquatMarketingProduct?sid={proid}'
        al_url = f'https://m.vodafone.com.tr/squat/updateSquatMarketingProduct?sid={proid}'
        
        try:
            cark_response = requests.post(cark_url, headers=o_head, json=cark_data)
            cark_response.raise_for_status()  # HTTP hata kodlarını yakalar
            cark = cark_response.json()
            
            if cark.get('result') == 'FAIL':
                error_message = cark.get('message', {}).get('message', 'Bilinmeyen hata oluştu.')
                bot.reply_to(message, f"API Yanıtı: {error_message}")
                bot.reply_to(message, 'Lütfen bir süre bekleyin ve tekrar deneyin.')
                return

            c1 = cark['data'].get('name', 'Bilgi Yok')
            c2 = cark['data'].get('code', 'Bilgi Yok')
            c3 = cark['data'].get('interactionID', 'Bilgi Yok')
            c4 = cark['data'].get('identifier', 'Bilgi Yok')
            
            al_data = {
                'clientKey': 'AC491770-B16A-4273-9CE7-CA790F63365E',
                'clientVersion': '16.8.3',
                'code': '',
                'identifier': c4,
                'interactionId': c3,
                'language': 'tr',
                'operatingSystem': 'android'
            }
            al_response = requests.post(al_url, headers=o_head, json=al_data)
            al_response.raise_for_status()  # HTTP hata kodlarını yakalar
            al = al_response.json()
            
            bot.reply_to(message, f"API Yanıtı: {json.dumps(al, indent=2)}")
            bot.reply_to(message, f'✅ {c1}\nEğer Varsa İndirim Kodunuz: {c2}')
            gg = bot.reply_to(message, "Koda Devam etmek için 'h' yaz: ")
            bot.register_next_step_handler(gg, lambda m: handle_next_step(m))

        except requests.exceptions.RequestException as e:
            bot.reply_to(message, f'Bir hata oluştu: {str(e)}')
        except KeyError as e:
            bot.reply_to(message, f'Bir hata oluştu: {str(e)}')

    elif sec == '2':
        bot.reply_to(message, '𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗞𝗔𝗡𝗔𝗟𝗜𝗡𝗔 𝗞𝗔𝗧𝗜𝗟 𝗢𝗡𝗖𝗘.')
        bot.send_message(message.chat.id, '𝗞𝗔𝗡𝗔𝗟𝗜𝗠𝗜𝗔 𝗕𝗘𝗞𝗟𝗘𝗥𝗜𝗭:  https://t.me/freeinternetv1')

        # Kanalda katılım kontrolü
        user_id = message.from_user.id
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)

        if chat_member.status in ['member', 'administrator', 'creator']:
            bot.reply_to(message, '𝗞𝗔𝗡𝗔𝗟𝗔 𝗞𝗔𝗧𝗜𝗟𝗗𝗜𝗡 𝗕𝗢𝗧𝗨 𝗞𝗨𝗟𝗟𝗔𝗡 𝗘𝗚𝗘𝗥 𝗞𝗔𝗡𝗔𝗟𝗗𝗔𝗡 𝗖𝗜𝗞𝗔𝗥𝗦𝗔𝗡 𝗕𝗜𝗥𝗗𝗔𝗛𝗔 𝗕𝗢𝗧𝗨𝗞𝗨𝗟𝗟𝗔𝗡𝗔𝗠𝗔𝗭𝗦𝗜𝗡')
        else:
            bot.reply_to(message, '𝗞𝗔𝗡𝗔𝗟𝗜𝗠𝗜𝗭𝗔 𝗕𝗘𝗞𝗟𝗘𝗥𝗜𝗭.')
            bot.send_message(message.chat.id, '𝗞𝗔𝗡𝗔𝗟𝗜𝗠𝗜𝗭𝗔 𝗞𝗔𝗧𝗜𝗟𝗗𝗜𝗚𝗜𝗡𝗜𝗭𝗗𝗔 𝗜𝗦𝗟𝗘𝗠 𝗧𝗔𝗠𝗔𝗠𝗟𝗔𝗡𝗔𝗖𝗔𝗞𝗧𝗜𝗥')

def handle_next_step(message):
    if message.text.lower() == 'h':
        bot.reply_to(message, 'Seçeneklere Yönlendiriyorum...')
        # Burada seçeneklerinizi kullanıcıya sunabilirsiniz.
        msg = bot.reply_to(message, 'Lütfen bir seçenek girin:\n\n[1] Yeni işlem\n[2] Yardım')
        bot.register_next_step_handler(msg, process_additional_actions)
    else:
        bot.reply_to(message, 'Yanlış yazdınız.')

def process_additional_actions(message):
    option = message.text

    if option == '1':
        bot.reply_to(message, 'Yeni işlem seçildi.')
        # Burada yeni işlem kodunuzu ekleyebilirsiniz.
    elif option == '2':
        bot.reply_to(message, 'Yardım seçildi.')
        # Burada yardım bilgilerini sağlayabilirsiniz.
    else:
        bot.reply_to(message, 'Geçersiz seçenek. Lütfen tekrar deneyin.')

# Botu çalıştırma
bot.polling()