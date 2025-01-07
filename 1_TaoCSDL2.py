import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Tạo cơ sở dữ liệu SQLite
def create_database():
    conn = sqlite3.connect("dantri_articles.db")
    cursor = conn.cursor()

    # Tạo bảng lưu thông tin bài báo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            summary TEXT,
            content TEXT,
            is_published INTEGER,
            Predict REAL,
            image_url TEXT
                
        )
    """)
    conn.commit()
    conn.close()
    print("Database and table created successfully!")

# Lưu dữ liệu bài báo vào cơ sở dữ liệu
def save_article_to_db(url, title, summary, content, image_url):
    conn = sqlite3.connect("dantri_articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO articles (url, title, summary, content, image_url)
        VALUES (?, ?, ?, ?, ?)
    """, (url, title, summary, content, image_url))

    conn.commit()
    conn.close()
    print(f"Article saved to database: {url}")

# Hàm thu thập nội dung bài báo
def scrape_article_content(url):
    print(f"Fetching article content from: {url}")
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)  # Đợi trang tải xong
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Lấy tiêu đề, nội dung, và ảnh
    title = soup.find('meta', property='og:title')
    title = title["content"] if title else "No Title"
    
    summary = soup.find('meta', property='og:description')
    summary = summary["content"] if summary else "No Summary"
    
    content_div = soup.find("div", class_="singular-content")
    content = "\n".join([p.text for p in content_div.find_all("p")]) if content_div else "No Content"
    
    image_tag = soup.find('meta', property='og:image')
    image_url = image_tag["content"] if image_tag else "No Image"

    return title, summary, content, image_url

# Hàm chính
def scrape_dantri_to_db():
    # URL chính để lấy các bài báo
    base_url = "https://dantri.com.vn/tam-long-nhan-ai.htm"
    driver = webdriver.Chrome()
    driver.get(base_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Lấy danh sách URL bài báo
    articles = soup.find_all("div", class_="news-item")  # Tùy thuộc vào cấu trúc trang web
    print(f"Found {len(articles)} articles on the page.")

    for article in articles:
        try:
            article_url = article.find("a")["href"]
            full_url = f"https://dantri.com.vn{article_url}" if article_url.startswith("/") else article_url
            
            # Lấy nội dung bài báo
            title, summary, content, image_url = scrape_article_content(full_url)
            
            # Lưu vào cơ sở dữ liệu
            save_article_to_db(full_url, title, summary, content, image_url)
        except Exception as e:
            print(f"Error processing article: {e}")

# Tạo cơ sở dữ liệu và chạy thu thập dữ liệu
if __name__ == "__main__":
    create_database()
    #scrape_dantri_to_db()