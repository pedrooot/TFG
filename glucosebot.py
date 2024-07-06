import requests
import schedule
from src.glucose import glucose_value
from utils.additional_funcions import load_config
from lib.cli.parser import GlucoseBotArgumentParser
import requests
from datetime import datetime, timedelta
import time 

def bot_send_text(bot_token, bot_chatID, bot_message):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def report():
    #Glucose results
    actual_glucose, previous_glucose, last_time = glucose_value()
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

    #check the time
    current_time = datetime.now().time()
    current_time = current_time.strftime("%H:%M:%S")
    # Change the format time to 12 hours
    current_time = datetime.strptime(current_time, "%H:%M:%S")
    current_time = current_time.strftime("%I:%M %p")

    # apply correct format for the last time and add 30 minutes
    last_time = last_time.split(" ")[1]
    last_time = datetime.strptime(last_time, "%H:%M:%S")
    last_time = last_time + timedelta(minutes=30)
    last_time = last_time.strftime("%H:%M:%S")
    # compare the last time with the current time knowing that the last time is in the format HH:MM:SS
    print(f"Current time: {current_time}, Last time: {last_time}")
    if current_time > last_time:
        glucose_result = "No data for the last 30 minutes, please check the device."

    config = load_config('config.yaml')
    response = bot_send_text(config['TELEGRAM_TOKEN'], config['USER_TELEGRAM_CHAT_ID'], glucose_result)
    if response.get("ok", False):
        print("Message sent successfully to user bot")
    else:
        if response.get("ok", False) == False:
            print("Message not sent due to invalid chat id or token")
            exit(1)
        else:
            print("Message not sent")
            exit(1)

    # Handle case for hospital bot
    response_hospital = {}
    if actual_glucose < config['MIN_GLUCOSE']:
        email = config['EMAIL']
        glucose_result = f'User {email} glucose level {actual_glucose} needs help'
        response_hospital = bot_send_text(config['HOSPITAL_TELEGRAM_BOT_TOKEN'], config['HOSPITAL_TELEGRAM_CHAT_ID'], glucose_result)
    # Handle case for hospital bot
    if response_hospital:
        if response_hospital.get("ok", False):
            print("Message sent successfully to hospital bot")
        else:
            while not response_hospital.get("ok", False):
                response_hospital = bot_send_text(config['HOSPITAL_TELEGRAM_BOT_TOKEN'], config['HOSPITAL_TELEGRAM_CHAT_ID'], glucose_result)
                print("Message not sent to hospital bot, trying again in 10 seconds")
                time.sleep(10)


def glucose_bot():
    parser = GlucoseBotArgumentParser()
    args = parser.parse()
    config = load_config('config.yaml')

    schedule.every(config['INTERVAL']).minutes.do(report)
    
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    glucose_bot()
