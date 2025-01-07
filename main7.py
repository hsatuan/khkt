import sqlite3 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

    # Lấy tiêu đề bài viết
    title = None
    if soup.find("meta", {"property": "og:title"}):
        title = soup.find("meta", {"property": "og:title"}).get('content', "No Title")
    elif soup.title:
        title = soup.title.text.strip()
    else:
        title = "No Title"

    # Lấy tóm tắt bài viết
    summary = None
    if soup.find("meta", {"name": "description"}):
        summary = soup.find("meta", {"name": "description"}).get('content', "No Summary")
    else:
        summary = "No Summary"

    # Lấy URL ảnh
    image_url = None
    if soup.find("meta", {"property": "og:image"}):
        image_url = soup.find("meta", {"property": "og:image"}).get('content', "No Image")
    else:
        image_url = "No Image"

    # Lấy nội dung bài viết
    content = None
    content_div = (
        soup.find("article") or
        soup.find("div", {"class": ["article-body", "content-detail", "main-content"]}) or
        soup.find("section", {"class": "content-detail"})
    )
    if content_div:
        content = "\n".join(p.text.strip() for p in content_div.find_all("p"))
        print(f"Content: {content[:50]}")  # In 50 ký tự đầu tiên để kiểm tra
    else:
        content = "No Content"

    return title, summary, content, image_url

def scrape_articles_from_url(url, limit=100):
    """Thu thập danh sách bài viết từ một trang web và lưu vào cơ sở dữ liệu"""
    soup = GetPageContentWithSelenium(url)
    if not soup:
        print("Failed to fetch the page.")
        return

    article_blocks = soup.find_all("article")
    article_count = 0
    for block in article_blocks:
        if article_count >= limit:
            break
        url_tag = block.find("a")
        if not url_tag or not url_tag.get('href'):
            continue
        article_url = url_tag['href']
        if article_url.startswith('/'):
            article_url = url + article_url
        elif not article_url.startswith('http'):
            print(f"Skipping invalid URL: {article_url}")
            continue

        title, summary, content, image_url = scrape_article(article_url)
        save_article_to_db(article_url, title, summary, content, image_url)
        print(f"Title: {title}, Summary: {summary}, Image URL: {image_url}")
        article_count += 1

def scrape_multiple_sites(url_list, limit=100):
    """Thu thập bài viết từ nhiều trang web được cung cấp"""
    for url in url_list:
        try:
            print(f"Scraping articles from {url}...")
            scrape_articles_from_url(url, limit)
        except KeyboardInterrupt:
            print("Scraping interrupted by user.")
            break
        except Exception as e:
            print(f"Error while scraping {url}: {e}")

if __name__ == "__main__":
    create_database()

    # Danh sách các URL trang web mà người dùng muốn tìm kiếm bài viết
    url_list = [
        "https://dantri.com.vn/tam-long-nhan-ai.htm"
        "https://vnexpress.net/topic/hoan-canh-kho-khan-17453",
        "https://thanhnien.vn/hoan-canh-kho-khan-tags504609.html?",
        "https://laodong.vn/tlv-canh-doi",
        
    ]

    scrape_multiple_sites(url_list)
