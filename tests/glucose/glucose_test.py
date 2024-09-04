import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.glucose import (
    get_cgm_data,
    get_patient_connections,
    glucose_value,
    login,
    requests,
)


@pytest.fixture
def mock_database():
    # Crear un mock para la base de datos
    db = MagicMock()
    return db


def test_login_successful():
    # Simula una respuesta exitosa de la API
    with patch("src.glucose.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"authTicket": {"token": "fake_token"}}
        }
        mock_post.return_value = mock_response

        token = login("test@example.com", "password123")

        assert token == None


def test_login_failure():
    # Simula una excepción de fallo en el login
    with patch("src.glucose.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.HTTPError("Login failed")

        with pytest.raises(requests.exceptions.HTTPError):
            login("test@example.com", "wrong_password")


def test_get_patient_connections():
    # Simula la obtención de conexiones del paciente
    with patch("src.glucose.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"patientId": "12345"}]}
        mock_get.return_value = mock_response

        token = "fake_token"
        result = get_patient_connections(token)

        assert result == {"data": [{"patientId": "12345"}]}


def test_get_cgm_data():
    # Simula la obtención de datos de glucosa
    with patch("src.glucose.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "graphData": [
                    {"Value": 100, "Timestamp": "08/28/2024 12:00:00 AM"},
                    {"Value": 95, "Timestamp": "08/28/2024 11:50:00 PM"},
                ]
            }
        }
        mock_get.return_value = mock_response

        token = "fake_token"
        patient_id = "12345"
        result = get_cgm_data(token, patient_id)

        assert result == {
            "data": {
                "graphData": [
                    {"Value": 100, "Timestamp": "08/28/2024 12:00:00 AM"},
                    {"Value": 95, "Timestamp": "08/28/2024 11:50:00 PM"},
                ]
            }
        }


def test_glucose_value_recent_scan(mock_database):
    # Simula que el último escaneo es reciente
    tiempo_actual = datetime.now()
    mock_database.get_last_escaneo_usuario.return_value = [(1, 100, 95, tiempo_actual)]

    result = glucose_value(1, mock_database)

    assert result == (100, 95, tiempo_actual)


def test_glucose_value_old_scan(mock_database):
    # Simula que el último escaneo es antiguo y se obtienen nuevos datos desde la API
    tiempo_actual = datetime.now()
    mock_database.get_last_escaneo_usuario.return_value = [
        (1, 100, 95, tiempo_actual - timedelta(hours=2))
    ]

    with patch(
        "src.glucose.get_patient_connections"
    ) as mock_get_patient_connections, patch(
        "src.glucose.get_cgm_data"
    ) as mock_get_cgm_data:

        mock_get_patient_connections.return_value = {"data": [{"patientId": "12345"}]}
        mock_get_cgm_data.return_value = {
            "data": {
                "graphData": [
                    {"Value": 105, "Timestamp": "08/28/2024 12:00:00 AM"},
                    {"Value": 100, "Timestamp": "08/28/2024 11:50:00 PM"},
                ]
            }
        }

        token = "fake_token"
        result = glucose_value(1, mock_database, token=token)

        assert result == (
            100,
            105,
            datetime.strptime("08/28/2024 11:50:00 PM", "%m/%d/%Y %I:%M:%S %p"),
        )
        mock_database.add_escaneo.assert_called_with(
            100,
            105,
            datetime.strptime("08/28/2024 11:50:00 PM", "%m/%d/%Y %I:%M:%S %p"),
            1,
        )


def test_glucose_value_no_token(mock_database):
    # Simula la ausencia de un token y por lo tanto no se puede obtener la glucosa
    mock_database.get_last_escaneo_usuario.return_value = []

    result = glucose_value(1, mock_database, token=None)

    assert result == (None, None, None)
