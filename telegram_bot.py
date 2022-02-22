import requests
from datetime import datetime

def telegram_bot_sendtext(bot_message):
    
    bot_token = '5008747919:AAFHUtlkYYO68Aa2dTZCFFGHFZB4D6kI8nA'
    bot_chatID = '242376372'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()
    

# now = datetime.now()
# def_date_time = now.strftime("%Y%m%d-%H%M%S-%fZ")
# test = telegram_bot_sendtext(f"{now}- Richiesta captcha")
# print(test)