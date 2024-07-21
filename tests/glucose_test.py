from datetime import datetime
from unittest.mock import Mock, patch
from src.glucose import glucose_value

@patch('src.glucose.get_cgm_data')
def test_glucose_value(mocked_get_cgm_data):

    current_time = datetime.now()
    mocked_get_cgm_data.return_value = {'data': {'graphData': [{'Value': 100}, {'Value': 90}, {'Time': current_time}]}}
    
    database = Mock()
    database.get_last_escaneo_usuario.return_value = {'ultimo_escaneo': current_time, 'valor_actual': 100, 'valor_previo': 90}
    actual_glucose, previous_glucose, last_time = glucose_value(user_id='test_user_id', database=database)

    assert actual_glucose == 100
    assert previous_glucose == 90
    assert last_time == current_time
