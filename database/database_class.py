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
        self.create_tables(database_name=database)

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

    def create_tables(self, database_name):
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
                token VARCHAR(255) NOT NULL,
                hospital_id INT,
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
