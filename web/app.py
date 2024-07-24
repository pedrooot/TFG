from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="tu_usuario_mysql",
        password="tu_contraseña_mysql",
        database="mi_proyecto"
    )
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    nombre = request.form['nombre']
    password = request.form['password']
    telegram_token = request.form['telegram_token']
    telegram_chat_id = request.form['telegram_chat_id']
    hospital_id = request.form['hospital_id']
    min_glucosa = request.form['min_glucosa']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Usuarios (nombre, password, telegram_token, telegram_chat_id, hospital_id, min_glucosa)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (nombre, password, telegram_token, telegram_chat_id, hospital_id, min_glucosa))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/register_hospital', methods=['POST'])
def register_hospital():
    nombre = request.form['nombre']
    idchat = request.form['idchat']
    token = request.form['token']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Hospitales (nombre, idchat, token)
                      VALUES (%s, %s, %s)''',
                   (nombre, idchat, token))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    # Aquí iría la lógica de login
    return "Login functionality not implemented yet"

if __name__ == '__main__':
    app.run(debug=True)
