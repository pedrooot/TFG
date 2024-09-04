from datetime import datetime, timedelta

import requests

# Constantes para la conexion con la API de Libreview
BASE_URL = "https://api-eu.libreview.io"
HEADERS = {
    "accept-encoding": "gzip",
    "cache-control": "no-cache",
    "connection": "Keep-Alive",
    "content-type": "application/json",
    "product": "llu.android",
    "version": "4.7",
}


# Funcion para hacer login y obtener el token de Libreview
def login(email, password):
    """Funcion para hacer login y obtener el token de Libreview
    Args:
        email (str): Email del usuario
        password (str): Contraseña del usuario
    Returns:
        str: Token de autenticacion
    """
    endpoint = "/llu/auth/login"
    payload = {"email": email, "password": password}

    response = requests.post(BASE_URL + endpoint, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    if len(data["data"]) > 0:
        auth_ticket = data["data"].get("authTicket")
        if auth_ticket:
            token = auth_ticket.get("token")
            return token
    return None


# Funcion para obtener las conexiones de un paciente
def get_patient_connections(token):
    """Funcion para obtener las conexiones de un paciente
    Args:
        token (str): Token de autenticacion
    Returns:
        dict: Datos del paciente
    """
    endpoint = "/llu/connections"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    response = requests.get(BASE_URL + endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


# Funcion para obtener los datos de la glucosa de un paciente
def get_cgm_data(token, patient_id):
    """Funcion para obtener los datos de la glucosa de un paciente
    Args:
        token (str): Token de autenticacion
        patient_id (str): ID del paciente
    Returns:
        dict: Datos de la glucosa del paciente
    """
    endpoint = f"/llu/connections/{patient_id}/graph"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    response = requests.get(BASE_URL + endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


# Funcion para obtener el valor de la glucosa de un paciente
def glucose_value(user_id, database, token=None):
    """Funcion para obtener el valor de la glucosa de un paciente
    Args:
        user_id (int): ID del usuario
        database (Database): Instancia de la base de datos
        token (str): Token de autenticacion
    Returns:
        tuple: Valor de la glucosa, valor previo y hora del ultimo escaneo
    """
    # Obtener el ultimo escaneo del usuario
    last_scan = database.get_last_escaneo_usuario(user_id)
    # Obtener el valor de la glucosa, el valor previo y la hora del ultimo escaneo
    last_scan_datetime = last_scan[0][3] if last_scan else None

    if (
        last_scan_datetime is not None
        and last_scan_datetime > datetime.now() - timedelta(minutes=30)
    ):
        return last_scan[0][1], last_scan[0][2], last_scan_datetime
    else:
        #  Si hay un token, obtener los datos del paciente
        if token:
            patient_data = get_patient_connections(token)

            patient_id = patient_data["data"][0]["patientId"]
            cgm_data = get_cgm_data(token, patient_id)
            # Take the last glucose value
            last_glucose = cgm_data["data"]["graphData"][-1]["Value"]
            previous_glucose = cgm_data["data"]["graphData"][-2]["Value"]
            # Take the hour of the last glucose value
            last_hour = cgm_data["data"]["graphData"][-1]["Timestamp"]
            # Put last_hour in the correct format
            last_hour = datetime.strptime(last_hour, "%m/%d/%Y %I:%M:%S %p")
            database.add_escaneo(last_glucose, previous_glucose, last_hour, user_id)
            return last_glucose, previous_glucose, last_hour
        else:
            return None, None, None
