from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('C:\\Users\\nikul\\PycharmProjects\\online_flower_shop\\flower_shop.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY, user_id INTEGER, bouquet_id INTEGER, quantity INTEGER, FOREIGN KEY(user_id) REFERENCES registration(id), FOREIGN KEY (bouquet_id) REFERENCES bouquets(id))")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS bouquets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL NOT NULL)")
    conn.commit()
    conn.close()

@app.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        with sqlite3.connect('C:\\Users\\nikul\\PycharmProjects\\online_flower_shop\\flower_shop.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM bouquets")
            rows = cursor.fetchall()
            catalog_b = [{"id": row[0], "name": row[1], "price": row[2]} for row in rows]
            return jsonify(catalog_b)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cart', methods=['POST'])
def add_to_cart():
    # Получаем данные из запроса
    data = request.get_json()
    user_id = str(data.get("user_id"))
    bouquet_id = data.get("bouquet_id")
    quantity = data.get("quantity", 1)
    if not user_id or not bouquet_id:
        return jsonify({"error": "user_id и bouquet_id обязательны"}), 400

    try:
        # Подключение к базе данных
        conn = sqlite3.connect('C:\\Users\\nikul\\PycharmProjects\\online_flower_shop\\flower_shop.db')
        cursor = conn.cursor()

        # Проверяем, есть ли уже такой товар в корзине пользователя
        cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND bouquet_id = ?",(user_id, bouquet_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Если товар уже есть, обновляем количество
            new_quantity = existing_item[0] + quantity
            cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND bouquet_id = ?",(new_quantity, user_id, bouquet_id))
            conn.commit()
            message = "Товар обновлён в корзине"
        else:
            # Если товара нет, добавляем новую запись
            cursor.execute("INSERT INTO cart (user_id, bouquet_id, quantity) VALUES (?, ?, ?)",(user_id, bouquet_id, quantity))
            conn.commit()
            message = "Товар добавлен в корзину"
        # Закрываем соединение
        conn.close()

        return jsonify({"message": message}), 201
    except Exception as e:
        return jsonify({"error": f"Ошибка работы с базой данных: {e}"}), 500

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    conn = sqlite3.connect('C:\\Users\\nikul\\PycharmProjects\\online_flower_shop\\flower_shop.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT bouquets.name, bouquets.price, cart.quantity FROM bouquets JOIN cart ON cart.bouquet_id = bouquets.id WHERE cart.user_id=?",
        (user_id,))
    items = cursor.fetchall()
    conn.close()
    formatted_items = [{"name": item[0], "price": item[1], "quantity": item[2]} for item in items]
    return jsonify(formatted_items), 200


@app.route('/cart/<int:id>', methods=['DELETE'])
def delete_bouquet_from_cart(id):
    try:
        conn = sqlite3.connect('C:\\Users\\nikul\\PycharmProjects\\online_flower_shop\\flower_shop.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE rowid IN (SELECT rowid FROM cart LIMIT 1 OFFSET ?)", (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Bouquet not found in cart!"}), 404
        conn.commit()
        return jsonify({"message": "Bouquet removed from cart!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)
