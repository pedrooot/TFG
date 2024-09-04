import hashlib
import json
import os
import sys

import bcrypt
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, redirect, render_template, request, session, url_for

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database_class import Database
from glucosebot import glucose_bot

app = Flask(__name__)


def get_secret(secret_name):
    """Función para obtener secretos desde AWS Secrets Manager"""
    client = boto3.client("secretsmanager")

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
        return json.loads(secret)
    except (NoCredentialsError, PartialCredentialsError):
        print("Credenciales no disponibles.")
        return None


# Obtener las credenciales de la base de datos desde Secrets Manager

secret = get_secret(os.environ["SECRET_NAME"])

db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
db_user = secret["username"]
db_pass = secret["password"]

app.secret_key = os.urandom(24)


def get_db_connection():
    database = Database(db_host, db_user, db_pass, db_name)
    database.connect()
    return database


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register_user", methods=["POST"])
def register_user():
    nombre = request.form["nombre"]
    password = request.form["password"]
    telegram_token = request.form["telegram_token"]
    telegram_chat_id = request.form["telegram_chat_id"]
    hospital_id = request.form["hospital_id"]
    min_glucosa = request.form["min_glucosa"]
    max_glucosa = request.form["max_glucosa"]
    notificacion_tiempo = request.form["notificacion_tiempo"]

    hashed_user = hash_username(nombre)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_db_connection().conn
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Usuarios (nombre, password, telegram_token, telegram_chat_id, hospital_id, min_glucosa, max_glucosa, notificacion_tiempo)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            hashed_user,
            hashed_password,
            telegram_token,
            telegram_chat_id,
            hospital_id,
            min_glucosa,
            max_glucosa,
            notificacion_tiempo,
        ),
    )

    user_id = cursor.lastrowid
    session["user_id"] = user_id
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    nombre = request.form["nombre"]
    password = request.form["password"]

    verication = verify_usuario(nombre, password)

    if verication[0] and verication[1]:
        session["user_id"] = verication[1]
        return redirect(url_for("profile"))
    else:
        return "Login failed. Please check your credentials and try again."


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_id = session["user_id"]
    database = get_db_connection()

    conn = database.conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        return "User not found", 404

    return render_template("profile.html", user=user)


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_id = session["user_id"]
    nombre = request.form["nombre"]
    password = request.form["password"]
    telegram_token = request.form["telegram_token"]
    telegram_chat_id = request.form["telegram_chat_id"]
    hospital_id = request.form["hospital_id"]
    min_glucosa = request.form["min_glucosa"]
    max_glucosa = request.form["max_glucosa"]
    notificacion_tiempo = request.form["notificacion_tiempo"]

    hashed_name = hash_username(nombre)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_db_connection().conn
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Usuarios SET nombre = %s, password = %s, telegram_token = %s, telegram_chat_id = %s, hospital_id = %s, min_glucosa = %s, max_glucosa = %s, notificacion_tiempo = %s WHERE id = %s""",
        (
            hashed_name,
            hashed_password,
            telegram_token,
            telegram_chat_id,
            hospital_id,
            min_glucosa,
            max_glucosa,
            notificacion_tiempo,
            user_id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("profile"))


@app.route("/register_hospital", methods=["POST"])
def register_hospital():
    nombre = request.form["nombre"]
    idchat = request.form["idchat"]
    token = request.form["token"]

    conn = get_db_connection().conn
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Hospitales (nombre, idchat, token)
                      VALUES (%s, %s, %s)""",
        (nombre, idchat, token),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/start_bot", methods=["POST"])
def start_bot():
    print("Starting bot")
    print(session["bot_running"])
    if not session.get("bot_running", False):
        database = get_db_connection()
        input_password = request.form["bot_password"]
        input_username = request.form["bot_username"]
        values_user = verify_usuario(input_username, input_password)
        if values_user[0]:
            glucose_bot(database, values_user[1], input_username, input_password)
            session["bot_running"] = True
            session["user_id"] = values_user[1]
        else:
            return "Invalid password"
    return redirect(url_for("profile"))


@app.route("/stop_bot", methods=["POST"])
def stop_bot():
    glucose_bot(stop=True)
    session["bot_running"] = False
    return redirect(url_for("profile"))


def hash_username(username):
    return hashlib.sha256(username.encode("utf-8")).hexdigest()


def verify_usuario(nombre, password):
    conn = get_db_connection().conn
    cursor = conn.cursor()

    hashed_nombre = hash_username(nombre)

    cursor.execute(
        "SELECT password, id FROM Usuarios WHERE nombre = %s", (hashed_nombre,)
    )
    values = cursor.fetchone()

    if values is None:
        return False, None

    user = values[1]
    stored_hashed_password = values[0]

    if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
        return True, user
    else:
        return False, None


if __name__ == "__main__":
    app.run(debug=True)
