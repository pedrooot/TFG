import requests
import schedule
from src.glucose import glucose_value
from utils.additional_funcions import load_config

def bot_send_text(bot_token, bot_chatID, bot_message):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def report():
    #Glucose results
    actual_glucose, previous_glucose = glucose_value() 
    if actual_glucose > 180:
        glucose_result = f'Current: {actual_glucose}, HIGH'
    if actual_glucose < 70:
        glucose_result = f'Current: {actual_glucose}, LOW'
    if actual_glucose > 180 and previous_glucose > 180:
        glucose_result = f'Current: {actual_glucose}, STILL HIGH'
    if actual_glucose < 70 and previous_glucose < 70:
        glucose_result = f'Current:{actual_glucose}, STILL LOW'
    if actual_glucose > 70 and actual_glucose < 180:
        glucose_result = f'Current: {actual_glucose}, YEAH'

    #Glucose results add info if previous glucose is by 20 units higher or lower
    if actual_glucose - previous_glucose > 20:
        glucose_result = glucose_result + f', ⬆️'
    if previous_glucose - actual_glucose > 20:
        glucose_result = glucose_result + f', ⬇️'

    config = load_config('config.yaml')
    bot_send_text(config['telegram_token'], config['telegram_chat_id'], glucose_result)


if __name__ == '__main__':
    
    schedule.every(20).minutes.do(report)
    
    while True:
        schedule.run_pending()