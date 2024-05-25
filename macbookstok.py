import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import pandas as pd

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

# Ürün ekleme
def urun_ekle():
    def ekle():
        barkod = barkod_entry.get()
        isim = isim_entry.get()
        miktar = miktar_entry.get()

        if barkod and isim and miktar:
            try:
                miktar = int(miktar)
                conn = sqlite3.connect('stok_takip.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO urunler (barkod, isim, miktar) VALUES (?, ?, ?)",
                               (barkod, isim, miktar))
                conn.commit()
                conn.close()
                messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi.")
                ekle_pencere.destroy()
                urunleri_guncelle()
            except sqlite3.IntegrityError:
                messagebox.showerror("Hata", "Bu barkod zaten mevcut.")
            except ValueError:
                messagebox.showerror("Hata", "Miktar sayısal bir değer olmalıdır.")
        else:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")

    ekle_pencere = tk.Toplevel()
    ekle_pencere.title("Ürün Ekle")

    tk.Label(ekle_pencere, text="Barkod:").grid(row=0, column=0, padx=10, pady=10)
    barkod_entry = tk.Entry(ekle_pencere)
    barkod_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(ekle_pencere, text="İsim:").grid(row=1, column=0, padx=10, pady=10)
    isim_entry = tk.Entry(ekle_pencere)
    isim_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(ekle_pencere, text="Miktar:").grid(row=2, column=0, padx=10, pady=10)
    miktar_entry = tk.Entry(ekle_pencere)
    miktar_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Button(ekle_pencere, text="Ekle", command=ekle).grid(row=3, columnspan=2, pady=10)

# Ürün silme
def urun_sil():
    barkod = simpledialog.askstring("Barkod", "Silmek istediğiniz ürünün barkodunu girin:")
    if barkod:
        conn = sqlite3.connect('stok_takip.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM urunler WHERE barkod=?", (barkod,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Ürün başarıyla silindi.")
        urunleri_guncelle()
    else:
        messagebox.showerror("Hata", "Lütfen bir barkod girin.")

# Ürün güncelleme
def urun_guncelle():
    barkod = simpledialog.askstring("Barkod", "Güncellemek istediğiniz ürünün barkodunu girin:")
    yeni_miktar = simpledialog.askinteger("Yeni Miktar", "Yeni miktarı girin:")
    if barkod and yeni_miktar is not None:
        conn = sqlite3.connect('stok_takip.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE urunler SET miktar=? WHERE barkod=?", (yeni_miktar, barkod))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Ürün başarıyla güncellendi.")
        urunleri_guncelle()
    else:
        messagebox.showerror("Hata", "Lütfen barkod ve yeni miktarı girin.")

# Ürünleri listeleme ve güncelleme
def urunleri_guncelle():
    for i in tree.get_children():
        tree.delete(i)
    
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urunler")
    urunler = cursor.fetchall()
    conn.close()

    for urun in urunler:
        tree.insert("", "end", values=(urun[1], urun[2], urun[3]))

# Arama fonksiyonu
def urun_ara():
    arama_kriteri = arama_entry.get()
    for i in tree.get_children():
        tree.delete(i)
    
    conn = sqlite3.connect('stok_takip.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urunler WHERE barkod LIKE ? OR isim LIKE ?", (f"%{arama_kriteri}%", f"%{arama_kriteri}%"))
    urunler = cursor.fetchall()
    conn.close()

    for urun in urunler:
        tree.insert("", "end", values=(urun[1], urun[2], urun[3]))

# Excel'den ürün ekleme
def excelden_urun_ekle():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        try:
            df = pd.read_excel(file_path)
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
            messagebox.showinfo("Başarılı", "Ürünler başarıyla eklendi.")
            urunleri_guncelle()
        except Exception as e:
            messagebox.showerror("Hata", f"Ürünler eklenirken hata oluştu: {e}")

# Ana uygulama
def main():
    initialize_db()

    global tree, arama_entry

    root = tk.Tk()
    root.title("Stok Takip Programı")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    style.configure("Treeview", font=("Helvetica", 10))

    frame = tk.Frame(root)
    frame.pack(pady=20)

    arama_frame = tk.Frame(root)
    arama_frame.pack(pady=10)

    tk.Label(arama_frame, text="Ara:").pack(side=tk.LEFT, padx=10)
    arama_entry = tk.Entry(arama_frame)
    arama_entry.pack(side=tk.LEFT, padx=10)
    tk.Button(arama_frame, text="Ara", command=urun_ara).pack(side=tk.LEFT, padx=10)

    tree = ttk.Treeview(frame, columns=("Barkod", "İsim", "Miktar"), show="headings")
    tree.heading("Barkod", text="Barkod")
    tree.heading("İsim", text="İsim")
    tree.heading("Miktar", text="Miktar")
    tree.pack()

    urunleri_guncelle()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Ürün Ekle", command=urun_ekle).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Ürün Sil", command=urun_sil).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Ürün Güncelle", command=urun_guncelle).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Yenile", command=urunleri_guncelle).grid(row=0, column=3, padx=5)
    tk.Button(btn_frame, text="Excel'den Ürün Ekle", command=excelden_urun_ekle).grid(row=0, column=4, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
