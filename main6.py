import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_database():
    """Tạo cơ sở dữ liệu SQLite"""
    conn = sqlite3.connect("dantri_articles.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            summary TEXT,
            content TEXT,
            image_url TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database and table created successfully!")

def save_article_to_db(url, title, summary, content, image_url):
    """Lưu bài báo vào cơ sở dữ liệu"""
    conn = sqlite3.connect("dantri_articles.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO articles (url, title, summary, content, image_url)
            VALUES (?, ?, ?, ?, ?)
        """, (url, title, summary, content, image_url))
        conn.commit()
        print(f"Article saved: {url}")
    except Exception as e:
        print(f"Error saving article: {e}")
    finally:
        conn.close()
def GetPageContentWithSelenium(url):
    """Lấy nội dung HTML của trang web bằng Selenium"""
    if not url.startswith("http://") and not url.startswith("https://"):
        print(f"Invalid URL format: {url}")
        return None

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver-win64\chromedriver.exe")

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        html = driver.page_source
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"Error fetching page: {url}, Error: {e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

def scrape_article(url):
    """Thu thập thông tin từ bài viết"""
    soup = GetPageContentWithSelenium(url)
    if not soup:
        return None, None, None, None

    title = soup.find("meta", {"name": "title"})['content'] if soup.find("meta", {"name": "title"}) else "No Title"
    summary = soup.find("meta", {"name": "description"})['content'] if soup.find("meta", {"name": "description"}) else "No Summary"
    image_url = soup.find("meta", {"property": "og:image"})['content'] if soup.find("meta", {"property": "og:image"}) else "No Image"
    content_div = soup.find("div", class_="singular-content")
    content = "\n".join(p.text.strip() for p in content_div.find_all("p")) if content_div else "No Content"

    return title, summary, content, image_url

def scrape_articles():
    """Thu thập danh sách bài viết và lưu vào cơ sở dữ liệu"""
    base_url = "https://dantri.com.vn"
    soup = GetPageContentWithSelenium(f"{base_url}/tam-long-nhan-ai.htm")
    if not soup:
        print("Failed to fetch main page.")
        return

    article_blocks = soup.find_all("article")
    for block in article_blocks:
        url_tag = block.find("a")
        if not url_tag or not url_tag.get('href'):
            continue
        article_url = url_tag['href']
        if article_url.startswith('/'):
            article_url = base_url + article_url
            print(f"Processing URL: {article_url}")
        elif not article_url.startswith('http'):
            print(f"Skipping invalid URL: {article_url}")
            continue

        title, summary, content, image_url = scrape_article(article_url)
        save_article_to_db(article_url, title, summary, content, image_url)
        print(f"Title: {title}, Summary: {summary}, Image URL: {image_url}")

if __name__ == "__main__":
    create_database()
    scrape_articles()
