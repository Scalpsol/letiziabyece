from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Veritabanı bağlantısı ve tablo oluşturma
def initialize_db():
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS urunler
                      (id INTEGER PRIMARY KEY,
                       barkod TEXT UNIQUE,
                       isim TEXT,
                       miktar INTEGER)''')
    conn.commit()
    conn.close()

# Ürünleri listeleme
@app.route('/')
def index():
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urunler")
    urunler = cursor.fetchall()
    conn.close()
    return render_template('index.html', urunler=urunler)

# Ürün ekleme
@app.route('/add', methods=['POST'])
def add():
    barkod = request.form['barkod']
    isim = request.form['isim']
    miktar = request.form['miktar']
    if barkod and isim and miktar:
        try:
            miktar = int(miktar)
            conn = sqlite3.connect('stok_takip.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO urunler (barkod, isim, miktar) VALUES (?, ?, ?)",
                           (barkod, isim, miktar))
            conn.commit()
            conn.close()
            flash('Ürün başarıyla eklendi.')
        except sqlite3.IntegrityError:
            flash('Bu barkod zaten mevcut.', 'error')
        except ValueError:
            flash('Miktar sayısal bir değer olmalıdır.', 'error')
    else:
        flash('Lütfen tüm alanları doldurun.', 'error')
    return redirect(url_for('index'))

# Ürün silme
@app.route('/delete/<string:barkod>')
def delete(barkod):
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urunler WHERE barkod=?", (barkod,))
    conn.commit()
    conn.close()
    flash('Ürün başarıyla silindi.')
    return redirect(url_for('index'))

# Ürün güncelleme
@app.route('/update', methods=['POST'])
def update():
    barkod = request.form['barkod']
    yeni_miktar = request.form['miktar']
    if barkod and yeni_miktar:
        try:
            yeni_miktar = int(yeni_miktar)
            conn = sqlite3.connect('stok_takip.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE urunler SET miktar=? WHERE barkod=?", (yeni_miktar, barkod))
            conn.commit()
            conn.close()
            flash('Ürün başarıyla güncellendi.')
        except ValueError:
            flash('Miktar sayısal bir değer olmalıdır.', 'error')
    else:
        flash('Lütfen barkod ve yeni miktarı girin.', 'error')
    return redirect(url_for('index'))

# Ürün arama
@app.route('/search', methods=['GET'])
def search():
    arama_kriteri = request.args.get('query')
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urunler WHERE barkod LIKE ? OR isim LIKE ?", (f"%{arama_kriteri}%", f"%{arama_kriteri}%"))
    urunler = cursor.fetchall()
    conn.close()
    return render_template('index.html', urunler=urunler)

# Excel'den ürün ekleme
@app.route('/import', methods=['POST'])
def import_excel():
    file = request.files['file']
    if file:
        try:
            df = pd.read_excel(file)
            conn = sqlite3.connect('stok_takip.db')
            cursor = conn.cursor()
            for index, row in df.iterrows():
                barkod = str(row['Barkod'])
                isim = row['Isim']
                miktar = int(row['Miktar'])
                cursor.execute("INSERT OR IGNORE INTO urunler (barkod, isim, miktar) VALUES (?, ?, ?)",
                               (barkod, isim, miktar))
            conn.commit()
            conn.close()
            flash('Ürünler başarıyla eklendi.')
        except Exception as e:
            flash(f'Ürünler eklenirken hata oluştu: {e}', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
