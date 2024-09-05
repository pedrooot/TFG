import time
from datetime import datetime, timedelta

import requests
import schedule

from config.config import print_banner
from src.glucose import glucose_value, login

token = None


def bot_send_text(bot_token, bot_chatID, bot_message):
    """Funcion para enviar un mensaje a un bot de telegram
    Args:
        bot_token (str): Token del bot de telegram
        bot_chatID (str): Chat ID del bot de telegram
        bot_message (str): Mensaje a enviar
    Returns:
        dict: Respuesta de la API de telegram
    """
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chatID
        + "&parse_mode=Markdown&text="
        + bot_message
    )

    response = requests.get(send_text)
    return response.json()


def report(user_id, hospital_id, database, user_name, input_password):
    """Funcion para enviar un mensaje al usuario y al hospital
    Args:
        user_id (int): ID del usuario
        hospital_id (int): ID del hospital
        database (Database): Instancia de la base de datos
        user_name (str): Nombre del usuario
        input_password (str): Contraseña del usuario para hacer login con la API de Libreview
    Returns:
        None
    """
    user = database.get_usuario(user_id)
    if not user:
        print("Usuario no encontrado")
        exit(1)
    chat_id = user[0][4]
    token_telegram = user[0][3]

    global token
    if token is None:
        token = login(user_name, input_password)

    actual_glucose, previous_glucose, last_time = glucose_value(
        user_id=user_id, database=database, token=token
    )
    if actual_glucose > 180:
        glucose_result = f"Valor actual de glucosa: {actual_glucose}, Alerta: Alto"
    if actual_glucose < 70:
        glucose_result = f"Valor actual de glucosa: {actual_glucose}, Alerta: Bajo"
    if actual_glucose > 180 and previous_glucose > 180:
        glucose_result = f"Valor actual de glucosa: {actual_glucose}, Alerta: Aún alto"
    if actual_glucose < 70 and previous_glucose < 70:
        glucose_result = f"Valor actual: {actual_glucose}, Alerta: Aún bajo"
    if actual_glucose > 70 and actual_glucose < 180:
        glucose_result = (
            f"Valor actual: {actual_glucose}, Sigues dentro del rango normal"
        )

    # Añadir ingremento o decremento dependiendo de la diferencia anterior
    if actual_glucose - previous_glucose > 20:
        glucose_result = glucose_result + ", ⬆️"
    if previous_glucose - actual_glucose > 20:
        glucose_result = glucose_result + ", ⬇️"

    # Obtener la diferencia de tiempo entre el último escaneo y el tiempo actual
    current_time = datetime.now()
    diference = current_time - last_time
    # Si la diferencia es mayor a 30 minutos, enviar un mensaje de error
    if diference > timedelta(minutes=30):
        glucose_result = "No has realizado un escaneo en los últimos 30 minutos, comprueba tu dispositivo"

    response = bot_send_text(token_telegram, chat_id, glucose_result)
    if response.get("ok", False):
        print("Mensaje enviado correctamente al usuario")
    else:
        if not response.get("ok", False):
            print("Error en el envío del mensaje")
            exit(1)
        else:
            print("Un error desconocido ha ocurrido")
            exit(1)

    # Manejar caso para bot de hospital
    response_hospital = {}
    if actual_glucose < user[0][6] or actual_glucose > user[0][7]:
        hospital = database.get_hospital(hospital_id)
        glucose_result = f"El usuario {user_name} tiene el nivel de glucosa en: {actual_glucose} por favor revisar su estado"
        response_hospital = bot_send_text(
            hospital[0][3], hospital[0][2], glucose_result
        )
    # Si el mensaje no se envía correctamente, intentar de nuevo
    if response_hospital:
        if response_hospital.get("ok", False):
            print("Mensaje enviado correctamente al hospital")
        else:
            while not response_hospital.get("ok", False):
                response_hospital = bot_send_text(
                    hospital[0][3], hospital_id[0][2], glucose_result
                )
                print(
                    "Error en el envío del mensaje al hospital, intentando de nuevo en 10 segundos"
                )
                time.sleep(10)


def glucose_bot(
    database=None, user_id=None, input_username=None, input_password=None, stop=False
):
    """Funcion principal para el bot de glucosa
    Args:
        database (Database): Instancia de la base de datos
        user_id (int): ID del usuario
        input_password (str): Contraseña del usuario para hacer login con la API de Libreview
        stop (bool): Bandera para detener el bot
    Returns:
        None
    """
    if stop:
        schedule.clear(user_id)
        print("Bot stopped")
        return
    print_banner()
    current_user = database.get_usuario(user_id)
    hospital_id = current_user[0][5]
    current_user[0][8]
    schedule.every(0.1).minutes.do(
        lambda: report(
            user_id=user_id,
            hospital_id=hospital_id,
            database=database,
            user_name=input_username,
            input_password=input_password,
        )
    ).tag(user_id)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    glucose_bot()
