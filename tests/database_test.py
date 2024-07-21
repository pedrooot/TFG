import pytest
from unittest import mock
from unittest.mock import MagicMock, patch
from database.database_class import Database  # Asegúrate de que tu clase Database está en un módulo importable.

@pytest.fixture
def db():
    with patch('mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Creamos una instancia de Database y asignamos los mocks manualmente
        database = Database.__new__(Database)
        database.host = 'localhost'
        database.user = 'testuser'
        database.password = 'testpassword'
        database.database = 'testdatabase'
        database.conn = mock_conn
        database.cursor = mock_cursor
        yield database

        database.close()

def test_add_hospital(db):
    db.add_hospital('Hospital A', 'chat123', 'token123')
    db.cursor.execute.assert_called_with(
        '''INSERT INTO Hospitales (nombre, idchat, token)
            VALUES (%s, %s, %s)''', ('Hospital A', 'chat123', 'token123')
    )
    assert db.conn.commit.call_count == 1

def test_add_usuario(db):
    db.add_hospital('Hospital A', 'chat123', 'token123')
    db.conn.commit.reset_mock()  # Reset the commit mock to avoid counting previous commits
    db.add_usuario('Usuario A', 'token456', 1, 70)
    db.cursor.execute.assert_called_with(
        '''INSERT INTO Usuarios (nombre, token, hospital_id, min_glucosa)
            VALUES (%s, %s, %s, %s)''', ('Usuario A', 'token456', 1, 70)
    )
    assert db.conn.commit.call_count == 1

def test_add_escaneo(db):
    db.add_hospital('Hospital A', 'chat123', 'token123')
    db.add_usuario('Usuario A', 'token456', 1, 70)
    db.conn.commit.reset_mock()  # Reset the commit mock to avoid counting previous commits
    db.add_escaneo(100.0, 90.0, '2023-07-21 10:00:00', 1)
    db.cursor.execute.assert_called_with(
        '''INSERT INTO Escaneos (valor_actual, valor_previo, ultimo_escaneo, usuario_id)
            VALUES (%s, %s, %s, %s)''', (100.0, 90.0, '2023-07-21 10:00:00', 1)
    )
    assert db.conn.commit.call_count == 1

def test_get_hospital(db):
    db.get_hospital(1)
    db.cursor.execute.assert_called_with('SELECT * FROM Hospitales WHERE id = %s', (1,))

def test_get_usuario(db):
    db.get_usuario(1)
    db.cursor.execute.assert_called_with('SELECT * FROM Usuarios WHERE id = %s', (1,))

def test_get_all_usuarios(db):
    db.get_all_usuarios()
    db.cursor.execute.assert_called_with('SELECT * FROM Usuarios')

def test_set_token_usuario(db):
    db.set_token_usuario(1, 'newtoken456')
    db.cursor.execute.assert_called_with('UPDATE Usuarios SET token = %s WHERE id = %s', ('newtoken456', 1))
    assert db.conn.commit.call_count == 1
