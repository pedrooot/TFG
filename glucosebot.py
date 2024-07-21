import requests
import schedule
from src.glucose import glucose_value
from lib.cli.parser import GlucoseBotArgumentParser
from datetime import datetime, timedelta
from database.database_class import Database
import time 

def bot_send_text(bot_token, bot_chatID, bot_message):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def report(user_id, hospital_id, database):
    #Glucose results
    actual_glucose, previous_glucose, last_time = glucose_value(user_id=user_id, database=database)
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

    # Get the user id chat and token
    user = database.get_usuario(user_id)
    chat_id = user['idchat']
    token = user['token']
    user_name = user['nombre']
    response = bot_send_text(token, chat_id, glucose_result)
    if response.get("ok", False):
        print("Message sent successfully to user bot")
    else:
        if not response.get("ok", False):
            print("Message not sent due to invalid chat id or token")
            exit(1)
        else:
            print("Message not sent")
            exit(1)

    # Handle case for hospital bot
    response_hospital = {}
    if actual_glucose < user['min_glucose']:
        hospital = database.get_hospital(hospital_id)
        glucose_result = f'User {user_name} glucose level {actual_glucose} needs help'
        response_hospital = bot_send_text(hospital['token'], hospital_id["idchat"], glucose_result)
    # Handle case for hospital bot
    if response_hospital:
        if response_hospital.get("ok", False):
            print("Message sent successfully to hospital bot")
        else:
            while not response_hospital.get("ok", False):
                response_hospital = bot_send_text(hospital['token'], hospital_id["idchat"], glucose_result)
                print("Message not sent to hospital bot, trying again in 10 seconds")
                time.sleep(10)


def glucose_bot():
    parser = GlucoseBotArgumentParser()
    args = parser.parse()
    database = Database(host=args.database_host, user=args.database_user, password=args.database_password, database=args.database_name)

    all_users = database.get_all_usuarios()
    for user in all_users:
        user_id = user['id']
        hospital_id = user['hospital_id']
        schedule.every(5).minutes.do(report(user_id=user_id, hospital_id=hospital_id, database=database))
    
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    glucose_bot()
