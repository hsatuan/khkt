import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # Thêm dòng import này

# Tạo cơ sở dữ liệu SQLite để lưu trữ các bài viết/video
def create_database():
    conn = sqlite3.connect("facebook_posts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            summary TEXT,
            content TEXT,
            post_type TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database and table created successfully!")

# Lưu bài viết vào cơ sở dữ liệu
def save_post_to_db(url, title, summary, content, post_type):
    conn = sqlite3.connect("facebook_posts.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO posts (url, title, summary, content, post_type)
            VALUES (?, ?, ?, ?, ?)
        """, (url, title, summary, content, post_type))
        conn.commit()
        print(f"Post saved: {url}")
    except Exception as e:
        print(f"Error saving post: {e}")
    finally:
        conn.close()

# Lấy nội dung trang Facebook sử dụng Selenium
def get_page_content_with_selenium(url, driver):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return driver.page_source
    except Exception as e:
        print(f"Error fetching page: {url}, Error: {e}")
        return None

# Tìm kiếm bài viết/video theo từ khóa trên Facebook
def search_facebook_posts(driver, keyword):
    """Tìm kiếm các bài viết/video có chứa từ khóa trên Facebook"""
    facebook_url = f"https://www.facebook.com/search/top?q={keyword}"
    print(f"Searching for keyword: {keyword} at URL: {facebook_url}")
    content = get_page_content_with_selenium(facebook_url, driver)

    if content:
        return content
    else:
        print(f"Failed to retrieve content for keyword: {keyword}")
        return None

# Phân tích các bài viết/video từ kết quả tìm kiếm trên Facebook
def analyze_facebook_posts(page_source, keyword):
    """Phân tích bài viết và video từ kết quả tìm kiếm"""
    soup = BeautifulSoup(page_source, "html.parser")
    posts = []
    
    # Tìm các bài viết (có thể là bài viết, video) trên trang Facebook
    for post in soup.find_all("div", {"data-testid": "post_message"}):
        title = post.get_text(strip=True)
        url = post.find_parent("a")["href"] if post.find_parent("a") else "No URL"
        summary = title[:100]  # Lấy phần mô tả đầu tiên
        content = title  # Tạm coi nội dung là phần mô tả
        
        # Xác định loại bài viết (bài viết hoặc video)
        post_type = "Video" if "video" in title.lower() else "Post"
        
        posts.append((url, title, summary, content, post_type))
    
    return posts

# Chạy tìm kiếm và lưu kết quả vào cơ sở dữ liệu
def search_and_save_posts(driver, keywords):
    """Tìm kiếm và lưu các bài viết từ các từ khóa"""
    for keyword in keywords:
        try:
            print(f"Searching for posts with keyword: {keyword}")
            page_source = search_facebook_posts(driver, keyword)
            if page_source:
                posts = analyze_facebook_posts(page_source, keyword)
                for url, title, summary, content, post_type in posts:
                    save_post_to_db(url, title, summary, content, post_type)
            else:
                print(f"No content found for keyword: {keyword}")
        except KeyboardInterrupt:
            print("Search interrupted by user.")
            break
        except Exception as e:
            print(f"Error searching for posts with keyword {keyword}: {e}")

if __name__ == "__main__":
    # Cấu hình trình duyệt Selenium
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    create_database()

    # Các từ khóa cần tìm kiếm trên Facebook
    keywords = ["khó khăn", "hoàn cảnh", "ngặt nghèo", "túng thiếu"]
    
    search_and_save_posts(driver, keywords)

    driver.quit()
