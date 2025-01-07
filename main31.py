import requests
import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver  # Import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def GetPageContentWithSelenium(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)

        print(f"Fetching URL with Selenium: {url}")
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"Error fetching URL with Selenium: {url} - {e}")
        return None


def ScrapeArticleContent(url):
    if not url or not url.startswith('http'):
        print(f"Invalid URL: {url}")
        return "No Content", "No Image", "No Title"

    print(f"Fetching article content from: {url}")
    soup = GetPageContentWithSelenium(url)
    if not soup:
        print(f"Failed to fetch article page: {url}")
        return "No Content", "No Image", "No Title"

    # Tìm thẻ JSON-LD
    json_ld_script = soup.find("script", type="application/ld+json")
    if json_ld_script:
        try:
            json_ld = json.loads(json_ld_script.string)
            title = json_ld.get("headline", "No Title")
            content = json_ld.get("description", "No Content")
            image = json_ld.get("image", {}).get("url", "No Image")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON-LD: {e}")
            title, content, image = "No Title", "No Content", "No Image"
    else:
        print(f"No JSON-LD metadata found for: {url}")
        title, content, image = "No Title", "No Content", "No Image"

    return content, image, title

def ScrapeDanTriTamLongNhanAi():
    base_url = "https://dantri.com.vn"
    soup = GetPageContentWithSelenium(f"{base_url}/tam-long-nhan-ai.htm")
    if not soup:
        print("Failed to fetch main page.")
        return []

    article_blocks = soup.find_all("article")
    print(f"Found {len(article_blocks)} articles on main page.")

    articles = []
    for i, block in enumerate(article_blocks):
        print(f"\nProcessing article {i + 1}/{len(article_blocks)}")

        # Lấy URL bài viết
        article_url_tag = block.find("a")
        article_url = article_url_tag['href'] if article_url_tag else None
        if article_url and article_url.startswith('/'):
            article_url = f"{base_url}{article_url}"

        # Lấy nội dung, hình ảnh và tiêu đề từ JSON-LD
        content, image_url, title = ScrapeArticleContent(article_url)
        print(f"Title: {title}")
        print(f"Content length: {len(content)} characters")
        print(f"Image URL: {image_url}")

        articles.append({
            "title": title,
            "content": content,
            "image_url": image_url,
            "article_url": article_url,
        })

    return articles

def send_to_main_website(article):
    url = "http://localhost:5000/api/articles"  # URL API của website chính
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=article, headers=headers)
    if response.status_code == 200:
        print("Gửi bài viết thành công:", article['title'])
    else:
        print("Lỗi khi gửi bài viết:", response.text)

# Ví dụ bài viết
#article = {
#    "title": "Bài viết từ Dân trí",
#    "summary": "Tóm tắt bài viết từ Dân trí",
#    "content": "Nội dung chi tiết bài viết từ Dân trí",
#    "image_url": "https://via.placeholder.com/150"
#}
html_file = "nhung3.html"
def add_article_to_website(html_file, title, url, image_url):
    """Thêm bài viết vào website trung gian."""
    if not os.path.exists(html_file):
        print(f"File {html_file} không tồn tại!")
        return

    # Thẻ <div> mới cho bài viết
    article_html = f"""
    <div class="item" data-url="{url}">
        <img src="{image_url}" alt="{title}">
        <a href="#" >{title}</a>
    </div>
    """

    # Đọc nội dung HTML hiện tại
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Tìm thẻ <div class="left-columns">
    left_columns = soup.find('div', class_='left-columns')
    if left_columns:
        left_columns.append(BeautifulSoup(article_html, 'html.parser'))
    else:
        print("Không tìm thấy thẻ <div class='left-columns'> trong file HTML.")

    # Ghi lại nội dung HTML đã cập nhật
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Đã thêm bài viết: {title}")

articles = ScrapeDanTriTamLongNhanAi()
for article in articles:
    add_article_to_website(
        html_file, 
        article["title"], 
        article["article_url"], 
        article["image_url"]
    )
