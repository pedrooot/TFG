import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from glucosebot import bot_send_text, glucose_bot, report


def test_bot_send_text():
    # Simula una respuesta exitosa de la API de Telegram
    with patch("glucosebot.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_get.return_value = mock_response

        response = bot_send_text("fake_token", "fake_chat_id", "Test message")

        assert response == {"ok": True}


def test_report_high_glucose():
    # Simula los métodos de la base de datos y la respuesta de Telegram
    mock_database = MagicMock()
    mock_database.get_usuario.return_value = [
        (
            1,
            "pedro",
            "hashed_password",
            "fake_telegram_token",
            "fake_chat_id",
            1,
            70,
            180,
            10,
        )
    ]
    mock_database.get_last_escaneo_usuario.return_value = [
        (1, 200, 190, datetime.now() - timedelta(minutes=10))
    ]
    mock_database.get_hospital.return_value = [
        (1, "hospital_name", "hospital_chat_id", "hospital_token")
    ]

    with patch("glucosebot.bot_send_text") as mock_bot_send_text:
        mock_bot_send_text.return_value = {"ok": True}

        report(
            user_id=1,
            hospital_id=1,
            database=mock_database,
            user_name="pedro",
            input_password="fake_password",
        )

        assert mock_bot_send_text.called
        mock_bot_send_text.assert_any_call(
            "hospital_token",
            "hospital_chat_id",
            "El usuario pedro tiene el nivel de glucosa en: 200 por favor revisar su estado",
        )


def test_report_low_glucose():
    # Simula los métodos de la base de datos y la respuesta de Telegram
    mock_database = MagicMock()
    mock_database.get_usuario.return_value = [
        (
            1,
            "pedro",
            "hashed_password",
            "fake_telegram_token",
            "fake_chat_id",
            1,
            70,
            180,
            10,
        )
    ]
    mock_database.get_last_escaneo_usuario.return_value = [
        (1, 60, 65, datetime.now() - timedelta(minutes=10))
    ]
    mock_database.get_hospital.return_value = [
        (1, "hospital_name", "hospital_chat_id", "hospital_token")
    ]

    with patch("glucosebot.bot_send_text") as mock_bot_send_text:
        mock_bot_send_text.return_value = {"ok": True}

        report(
            user_id=1,
            hospital_id=1,
            database=mock_database,
            user_name="pedro",
            input_password="pedrotfg-1111P",
        )

        assert mock_bot_send_text.called
        mock_bot_send_text.assert_any_call(
            "hospital_token",
            "hospital_chat_id",
            "El usuario pedro tiene el nivel de glucosa en: 60 por favor revisar su estado",
        )


def test_glucose_bot_stop():
    # Simula que el bot se detiene
    with patch("glucosebot.schedule.clear") as mock_clear:
        with pytest.raises(SystemExit):
            glucose_bot(stop=True)

        mock_clear.assert_called_once()
