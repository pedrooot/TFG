import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from database.database_class import Database


@pytest.fixture
@patch("mysql.connector.connect")
def db(mock_connect):
    # Configura un mock para la conexión de la base de datos
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Inicializa la clase Database
    database = Database("localhost", "user", "password", "test_db")

    # Asigna mocks para usar en las pruebas
    database.mock_conn = mock_conn
    database.mock_cursor = mock_cursor
    return database


def test_connect(db):
    # Verifica que la conexión y el cursor se hayan inicializado
    db.connect()
    assert db.conn.is_connected()
    db.mock_conn.cursor.assert_called_once()


def test_create_database(db):
    # Simula la creación de la base de datos
    db.create_database("test_db")
    db.mock_cursor.execute.assert_any_call("CREATE DATABASE IF NOT EXISTS test_db")


def test_create_tables(db):
    # Simula la creación de las tablas
    db.create_tables()
    db.mock_cursor.execute.assert_any_call("SHOW TABLES")
    # Comprueba que se haya hecho commit 2 veces
    assert db.mock_conn.commit.call_count == 2


def test_add_escaneo(db):
    # Prueba la función para añadir un escaneo
    db.add_escaneo(100.5, 98.2, "2024-01-01 12:00:00", 1)
    db.mock_cursor.execute.assert_called_with(
        """INSERT INTO Escaneos (valor_actual, valor_previo, ultimo_escaneo, usuario_id)
            VALUES (%s, %s, %s, %s)""",
        (100.5, 98.2, "2024-01-01 12:00:00", 1),
    )
    # Comprueba que se haya hecho commit 2 veces
    assert db.mock_conn.commit.call_count == 2


def test_get_hospital(db):
    # Prueba la función para obtener un hospital
    db.mock_cursor.fetchall.return_value = [("Hospital 1", "chat_id", "token")]
    result = db.get_hospital(1)
    db.mock_cursor.execute.assert_called_with(
        "SELECT * FROM Hospitales WHERE id = %s", (1,)
    )
    assert result == [("Hospital 1", "chat_id", "token")]


def test_get_usuario(db):
    # Prueba la función para obtener un usuario
    db.mock_cursor.fetchall.return_value = [
        ("Usuario 1", "hashed_password", "telegram_token", "chat_id")
    ]
    result = db.get_usuario(1)
    db.mock_cursor.execute.assert_called_with(
        "SELECT * FROM Usuarios WHERE id = %s", (1,)
    )
    assert result == [("Usuario 1", "hashed_password", "telegram_token", "chat_id")]


def test_get_all_usuarios(db):
    # Prueba la función para obtener todos los usuarios
    db.mock_cursor.fetchall.return_value = [
        ("Usuario 1", "hashed_password", "telegram_token", "chat_id"),
        ("Usuario 2", "hashed_password", "telegram_token", "chat_id"),
    ]
    result = db.get_all_usuarios()
    db.mock_cursor.execute.assert_called_with("SELECT * FROM Usuarios")
    assert result == [
        ("Usuario 1", "hashed_password", "telegram_token", "chat_id"),
        ("Usuario 2", "hashed_password", "telegram_token", "chat_id"),
    ]
