import pytest
from unittest.mock import patch
import requests
from src.glucose import glucose_value

@pytest.fixture
def mocked_post_request():
    with patch('requests.post') as mocked_post:
        mocked_post.return_value.json.return_value = {'data': {'authTicket': {'token': 'test_token'}}}
        yield mocked_post

@pytest.fixture
def mocked_get_request():
    with patch('requests.get') as mocked_get:
        mocked_get.return_value.json.return_value = {'data': [{'patientId': 'test_patient_id'}]}
        yield mocked_get

@patch('src.glucose.get_cgm_data')
def test_glucose_value(mocked_get_cgm_data, mocked_post_request, mocked_get_request):

    mocked_get_cgm_data.return_value = {'data': {'graphData': [{'Value': 100}, {'Value': 90}, {'Time': 'test_time'}]}}
    

    actual_glucose, previous_glucose, last_time = glucose_value()
    mocked_post_request.assert_called_once()
    mocked_get_request.assert_called_once()
    mocked_get_cgm_data.assert_called_once()

    assert actual_glucose == 90
    assert previous_glucose == 100
    assert last_time == 'test_time'
