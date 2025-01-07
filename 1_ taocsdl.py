import sqlite3
import requests
from bs4 import BeautifulSoup

def save_urls_to_db(db_path, url):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Tạo bảng nếu chưa tồn tại
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                image_url TEXT,
                selected INTEGER DEFAULT 0 -- 0: chưa chọn, 1: đã chọn
            )
        ''')
        conn.commit()

        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP

        soup = BeautifulSoup(response.content, 'html.parser')

        for item in soup.find_all('div', class_='item'):
            data_url = item.get('data-url')
            if data_url:
                a_tag = item.find('a')
                title = a_tag.text.strip() if a_tag else ""
                img_tag = item.find('img')
                image_url = img_tag.get('src') if img_tag else ""
                try:
                    cursor.execute("INSERT INTO urls (url, title, image_url) VALUES (?, ?, ?)", (data_url, title, image_url))
                    conn.commit()
                    print(f"Added url {data_url} to database")
                except sqlite3.IntegrityError:
                    print(f"Url {data_url} already exists in database")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Ví dụ sử dụng:
db_path = 'urls.db'
url_dantri='https://dantri.com.vn/tam-long-nhan-ai.htm'
save_urls_to_db(db_path,url_dantri)