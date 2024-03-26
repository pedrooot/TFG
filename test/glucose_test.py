import pytest
from  utils.additional_funcions import load_config
from unittest.mock import patch
import requests
from src.glucose import glucose_value

# Fixture para cargar la configuración
@pytest.fixture
def mocked_load_config():
    with patch('utils.additional_funcions.load_config') as mocked_load_config:
        mocked_load_config.return_value = {'email': 'test@example.com', 'password': 'test_password'}
        yield mocked_load_config

# Fixture para simular la respuesta de la solicitud POST
@pytest.fixture
def mocked_post_request():
    with patch('requests.post') as mocked_post:
        mocked_post.return_value.json.return_value = {'data': {'authTicket': {'token': 'test_token'}}}
        yield mocked_post

# Fixture para simular la respuesta de la solicitud GET
@pytest.fixture
def mocked_get_request():
    with patch('requests.get') as mocked_get:
        mocked_get.return_value.json.return_value = {'data': [{'patientId': 'test_patient_id'}]}
        yield mocked_get

def test_glucose_value(mocked_load_config, mocked_post_request, mocked_get_request):
    # Ejecuta la función
    last_glucose, previous_glucose = glucose_value()

    # Verifica que la función devuelva valores esperados
    assert last_glucose == 'test_last_glucose'
    assert previous_glucose == 'test_previous_glucose'
