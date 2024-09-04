from errno import errorcode

import mysql.connector


class Database:
    """Clase para gestionar la base de datos
    Attributes:
        host (str): Host de la base de datos
        user (str): Usuario de la base de datos
        password (str): Contraseña de la base de datos
        database (str): Nombre de la base de datos
        conn (mysql.connector.connection.MySQLConnection): Conexion a la base de datos
        cursor (mysql.connector.cursor.MySQLCursor): Cursor de la base de datos
    """

    host = None
    user = None
    password = None
    database = None
    conn = None
    cursor = None

    def __init__(self, host, user, password, database):
        """Constructor de la clase Database
        Args:
            host (str): Host de la base de datos
            user (str): Usuario de la base de datos
            password (str): Contraseña de la base de datos
            database (str): Nombre de la base de datos
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.conn = None
        self.cursor = None
        # self.create_database(database)
        self.connect()
        self.create_tables()

    def connect(self):
        """Funcion para conectar a la base de datos
        Returns:
            None
        """
        if self.conn is None or not self.conn.is_connected():
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.conn.cursor()

    def close(self):
        """Funcion para cerrar la conexion a la base de datos
        Returns:
            None
        """
        self.cursor.close()
        self.conn.close()

    def create_database(self, database):
        """Funcion para crear la base de datos
        Args:
            database (str): Nombre de la base de datos
        Returns:
            None
        """
        try:
            if self.conn is None:
                self.connect()
            if self.cursor is None:
                self.cursor = self.conn.cursor()

            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
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
        """Funcion para crear las tablas de la base de datos
        Returns:
            None
        """
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
            if self.cursor is None:
                self.cursor = self.conn.cursor()

            # Comprobamos si existen las tablas
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            available_tables = [table[0] for table in tables]

            if "Hospitales" not in available_tables:
                self.cursor.execute(
                    """CREATE TABLE Hospitales (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(255) NOT NULL,
                    idchat VARCHAR(255) NOT NULL,
                    token VARCHAR(255) NOT NULL
                );"""
                )

            if "Usuarios" not in available_tables:
                self.cursor.execute(
                    """CREATE TABLE Usuarios (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    telegram_token VARCHAR(255) NOT NULL,
                    telegram_chat_id VARCHAR(255) NOT NULL,
                    hospital_id INT,
                    min_glucosa INT,
                    max_glucosa INT,
                    notificacion_tiempo INT,
                    FOREIGN KEY (hospital_id) REFERENCES Hospitales(id)
                );"""
                )

            if "Escaneos" not in available_tables:
                self.cursor.execute(
                    """CREATE TABLE Escaneos (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    valor_actual DECIMAL(10, 2) NOT NULL,
                    valor_previo DECIMAL(10, 2),
                    ultimo_escaneo DATETIME NOT NULL,
                    usuario_id INT,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
                );"""
                )

            self.conn.commit()
            print("Tablas creadas correctamente")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(
                    "Un error ha ocurrido con el usuario o la contraseña, por favor revisa los datos"
                )
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("La base de datos no existe")
            else:
                print(err)
        finally:
            self.cursor.close()
            self.conn.close()

    def con_and_cursor(self):
        """Funcion para conectar a la base de datos y obtener el cursor
        Returns:
            None
        """
        self.connect()
        self.cursor = self.conn.cursor()

    def add_escaneo(self, valor_actual, valor_previo, ultimo_escaneo, usuario_id):
        """Funcion para añadir un escaneo a la base de datos
        Args:
            valor_actual (float): Valor actual de la glucosa
            valor_previo (float): Valor previo de la glucosa
            ultimo_escaneo (str): Hora del ultimo escaneo
            usuario_id (int): ID del usuario
        Returns:
            None
        """
        self.con_and_cursor()
        self.cursor.execute(
            """INSERT INTO Escaneos (valor_actual, valor_previo, ultimo_escaneo, usuario_id)
            VALUES (%s, %s, %s, %s)""",
            (valor_actual, valor_previo, ultimo_escaneo, usuario_id),
        )

        self.conn.commit()

    def get_hospital(self, id):
        """Funcion para obtener un hospital de la base de datos
        Args:
            id (int): ID del hospital
        Returns:
            list: Datos del hospital
        """
        self.con_and_cursor()
        self.cursor.execute("SELECT * FROM Hospitales WHERE id = %s", (id,))
        return self.cursor.fetchall()

    def get_usuario(self, id):
        """Funcion para obtener un usuario de la base de datos
        Args:
            id (int): ID del usuario
        Returns:
            list: Datos del usuario
        """
        self.con_and_cursor()
        self.cursor.execute("SELECT * FROM Usuarios WHERE id = %s", (id,))
        return self.cursor.fetchall()

    def get_all_usuarios(self):
        """Funcion para obtener todos los usuarios de la base de datos
        Returns:
            list: Datos de todos los usuarios
        """
        self.con_and_cursor()
        self.cursor.execute("SELECT * FROM Usuarios")
        return self.cursor.fetchall()

    def get_last_escaneo_usuario(self, user_id):
        """Funcion para obtener el ultimo escaneo de un usuario
        Args:
            user_id (int): ID del usuario
        Returns:
            list: Datos del ultimo escaneo
        """
        self.con_and_cursor()
        self.cursor.execute(
            "SELECT * FROM Escaneos WHERE usuario_id = %s ORDER BY ultimo_escaneo DESC LIMIT 1",
            (user_id,),
        )
        return self.cursor.fetchall()
