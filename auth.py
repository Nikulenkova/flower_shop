from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect('C:\\flower_shop.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS registration (id INTEGER PRIMARY KEY, login TEXT NOT NULL, password TEXT NOT NULL)")
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    login = data['login']
    password = data['password']
    conn = sqlite3.connect('C:\\flower_shop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registration (login, password) VALUES (?, ?)", (login, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "Успешная регистрация"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data['login']
    password = data['password']
    conn = sqlite3.connect('C:\\flower_shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration WHERE login=? AND password=?", (login, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"id": user[0]}), 200
    else:
        return jsonify({"error": "Неверный логин или пароль"}), 400

if __name__ == '__main__':
    app.run(port=5000)
