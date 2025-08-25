from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'products.db'
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cria tabela se não existir
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            filename TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_products():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products_data = c.fetchall()
    products = []
    for p in products_data:
        pid, name, link = p
        c.execute('SELECT filename FROM images WHERE product_id=?', (pid,))
        images = [f"/static/{row[0]}" for row in c.fetchall()]
        products.append({'id': pid, 'name': name, 'link': link, 'images': images})
    conn.close()
    return products

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('productName')
            link = request.form.get('productLink')
            files = request.files.getlist('productImages')
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('INSERT INTO products (name, link) VALUES (?, ?)', (name, link))
            pid = c.lastrowid
            for f in files:
                if f.filename != '':
                    path = os.path.join(UPLOAD_FOLDER, f.filename)
                    f.save(path)
                    c.execute('INSERT INTO images (product_id, filename) VALUES (?, ?)', (pid, f.filename))
            conn.commit()
            conn.close()
        elif action == 'edit':
            pid = int(request.form.get('index'))
            name = request.form.get('productName')
            link = request.form.get('productLink')
            files = request.files.getlist('productImages')
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('UPDATE products SET name=?, link=? WHERE id=?', (name, link, pid))
            for f in files:
                if f.filename != '':
                    path = os.path.join(UPLOAD_FOLDER, f.filename)
                    f.save(path)
                    c.execute('INSERT INTO images (product_id, filename) VALUES (?, ?)', (pid, f.filename))
            conn.commit()
            conn.close()
        elif action == 'delete':
            pid = int(request.form.get('index'))
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('DELETE FROM images WHERE product_id=?', (pid,))
            c.execute('DELETE FROM products WHERE id=?', (pid,))
            conn.commit()
            conn.close()
        return redirect(url_for('index'))

    products = get_products()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


