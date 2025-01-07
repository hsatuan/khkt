import sqlite3

def add_is_published_column(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Kiểm tra xem cột đã tồn tại chưa
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    if "some_number_field" not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN some_number_field REAL")
        conn.commit()
        print("Đã thêm cột 'is_published' vào cơ sở dữ liệu.")
    else:
        print("Cột 'is_published' đã tồn tại trong cơ sở dữ liệu.")

    conn.close()

# Gọi hàm
add_is_published_column("dantri_articles.db")