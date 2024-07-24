from errno import errorcode
import mysql

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def create_database(self):
        try:
            if self.conn is None:
                self.connect()
            if self.cursor is None:
                self.cursor = self.conn.cursor()

            self.cursor.execute('CREATE DATABASE IF NOT EXISTS example_db')
            self.cursor.close()

            print("Database created successfully")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def create_tables(self):
        try:
            if self.conn is None:
                self.connect()
            if self.cursor is None:
                self.cursor = self.conn.cursor()

            self.cursor.execute('''CREATE TABLE Hospitales (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                idchat VARCHAR(255) NOT NULL,
                token VARCHAR(255) NOT NULL
            );''')

            self.cursor.execute('''CREATE TABLE Usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                telegram_token VARCHAR(255) NOT NULL,
                telegram_chat_id VARCHAR(255) NOT NULL,
                hospital_id INT,
                min_glucosa INT,
                FOREIGN KEY (hospital_id) REFERENCES Hospitales(id)
            );''')

            self.cursor.execute('''CREATE TABLE Escaneos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                valor_actual DECIMAL(10, 2) NOT NULL,
                valor_previo DECIMAL(10, 2),
                ultimo_escaneo DATETIME NOT NULL,
                usuario_id INT,
                FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
            );''')

            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            print("Tables created successfully")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)



    def add_hospital(self, nombre, idchat, token):
        self.cursor.execute('''INSERT INTO Hospitales (nombre, idchat, token)
            VALUES (%s, %s, %s)''', (nombre, idchat, token))

        self.conn.commit()

    def add_usuario(self, nombre, password, telegram_token, telegram_chat_id, hospital_id, min_glucosa):
        self.cursor.execute('''INSERT INTO Usuarios (nombre, password, token, hospital_id, min_glucosa)
            VALUES (%s, %s, %s, %s, %s, %s)''', (nombre, password, telegram_token, telegram_chat_id, hospital_id, min_glucosa))

        self.conn.commit()

    def add_escaneo(self, valor_actual, valor_previo, ultimo_escaneo, usuario_id):
        self.cursor.execute('''INSERT INTO Escaneos (valor_actual, valor_previo, ultimo_escaneo, usuario_id)
            VALUES (%s, %s, %s, %s)''', (valor_actual, valor_previo, ultimo_escaneo, usuario_id))

        self.conn.commit()

    def get_hospital(self, id):
        self.cursor.execute('SELECT * FROM Hospitales WHERE id = %s', (id,))
        return self.cursor.fetchall()
    
    def get_usuario(self, id):
        self.cursor.execute('SELECT * FROM Usuarios WHERE id = %s', (id,))
        return self.cursor.fetchall()

    def get_all_usuarios(self):
        self.cursor.execute('SELECT * FROM Usuarios')
        return self.cursor.fetchall()
    
    def get_escaneo(self, id):
        self.cursor.execute('SELECT * FROM Escaneos WHERE id = %s', (id,))
        return self.cursor.fetchall()
    
    def get_escaneos_usuario(self, usuario_id):
        self.cursor.execute('SELECT * FROM Escaneos WHERE usuario_id = %s', (usuario_id,))
        return self.cursor.fetchall()
    
    def get_escaneos_hospital(self, hospital_id):
        self.cursor.execute('SELECT * FROM Escaneos WHERE usuario_id IN (SELECT id FROM Usuarios WHERE hospital_id = %s)', (hospital_id,))
        return self.cursor.fetchall()
    
    def get_usuarios_hospital(self, hospital_id):
        self.cursor.execute('SELECT * FROM Usuarios WHERE hospital_id = %s', (hospital_id,))
        return self.cursor.fetchall()
    
    def get_hospital_usuario(self, usuario_id):
        self.cursor.execute('SELECT * FROM Hospitales WHERE id IN (SELECT hospital_id FROM Usuarios WHERE id = %s)', (usuario_id,))
        return self.cursor.fetchall()
    
    def get_last_escaneo_usuario(self, usuario_id):
        self.cursor.execute('SELECT * FROM Escaneos WHERE usuario_id = %s ORDER BY ultimo_escaneo DESC LIMIT 1', (usuario_id,))
        return self.cursor.fetchall()
    
    def get_last_date_escaneo_usuario(self, usuario_id):
        self.cursor.execute('SELECT ultimo_escaneo FROM Escaneos WHERE usuario_id = %s ORDER BY ultimo_escaneo DESC LIMIT 1', (usuario_id,))
        return self.cursor.fetchall()
    
    def set_token_usuario(self, usuario_id, token):
        self.cursor.execute('UPDATE Usuarios SET token = %s WHERE id = %s', (token, usuario_id))
        self.conn.commit()
    
    def get_token_usuario(self, usuario_id):
        self.cursor.execute('SELECT token FROM Usuarios WHERE id = %s', (usuario_id,))
        return self.cursor.fetchall()
