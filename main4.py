import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver  # Import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def GetPageContentWithSelenium(url):
    """Sử dụng Selenium để lấy nội dung HTML đầy đủ của một URL."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--ignore-certificate-errors')  # Bỏ qua lỗi SSL
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=chrome_options)   
        print(f"Fetching URL with Selenium: {url}")
        driver.get(url)
        content = driver.page_source
        # Cuộn xuống để tải nội dung lazy-load
        print("Page fetched successfully!")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"Error occurred while fetching URL: {url}")
        print(f"Error details: {e}")
        raise
        return None

def ScrapeArticleContent(url):
    """Lấy nội dung và hình ảnh từ một bài viết trên Dân trí."""
    print(f"Fetching URL: {url}")
    if not url or not url.startswith('http'):
        print(f"Invalid URL: {url}")
        return "No Content", "No Image"

    print(f"Fetching article content from: {url}")
    html_file="nhung3.html"
    
    # Thêm thẻ <div> mới chứa URL
    url_html = f"""
    <div class="item" data-url="{url}">
        <a href="{url}" target="_blank">{url}</a>
    </div>
    """
    print(f"URL HTML to add: {url_html}")
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        print(f"Đã đọc file HTML: {html_file}")

        left_columns = soup.find('div', class_='left-columns')
        if left_columns:
            left_columns.append(BeautifulSoup(url_html, 'html.parser'))
            print(f"Đã thêm URL vào thẻ <div class='left-columns'>.")
        else:
            print("Không tìm thấy thẻ <div class='left-columns'> trong file HTML.")

        # Ghi lại file HTML sau khi thêm URL
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"Đã thêm URL thành công: {url}")
    except Exception as e:
        print(f"Lỗi khi thêm URL vào file HTML: {e}")

    soup = GetPageContentWithSelenium(url)
    if not soup:
        print(f"Failed to fetch article page: {url}")
        return "No Content", "No Image"

    # Lấy nội dung bài viết
    content_div = soup.find("div", class_="singular-content")
    if not content_div:
        print(f"No content found for article: {url}")
        return "No Content", "No Image"

    paragraphs = content_div.find_all("p")
    content = "\n".join([p.text.strip() for p in paragraphs]) if paragraphs else "No Content"

    # Lấy URL hình ảnh
    image_tag = soup.find("img", class_="image align-center")
    image_url = None
    if image_tag:
        image_url = image_tag.get("data-src") or image_tag.get("data-original") or image_tag.get("src")
    return content, image_url or "No Image"

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

        # Lấy tiêu đề
        title_tag = block.find("a", class_="article-item__title")
        title = title_tag.text.strip() if title_tag else "No Title"
        print(f"Title: {title}")

        # Lấy URL bài viết
        article_url_tag = block.find("a")
        article_url = article_url_tag['href'] if article_url_tag else None
        if article_url:
            if article_url.startswith('/'):  # URL tương đối
                article_url = f"{base_url}{article_url}"
            elif not article_url.startswith('http'):  # URL sai định dạng
                article_url = f"{base_url}/{article_url}"
            print(f"Article URL: {article_url}")

        # Lấy tóm tắt
        summary_tag = block.find("div", class_="article-item__sapo")
        summary = summary_tag.text.strip() if summary_tag else "No Summary"
        print(f"Summary: {summary}")

        # Lấy nội dung và hình ảnh bài viết
        try:
            content, image_url = ScrapeArticleContent(article_url)
        except Exception as e:
            print(f"Error fetching content for article URL {article_url}: {e}")
            content, image_url = "No Content", "No Image"

        print(f"Content length: {len(content)} characters")
        print(f"Content: {content}")
        print(f"Image URL: {image_url}")

        articles.append({
            "title": title,
            "summary": summary,
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

def add_url_to_website(html_file, url):
    """Thêm URL vào website trung gian."""
    print(f"Starting to add URL to {html_file}")
    if not os.path.exists(html_file):
        print(f"File {html_file} không tồn tại!")
        return

    # Thêm thẻ <div> mới chứa URL
    url_html = f"""
    <div class="item" data-url="{url}">
        <a href="{url}" target="_blank">{url}</a>
    </div>
    """
    print(f"URL HTML to add: {url_html}")

    # Mở file HTML và thêm URL
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        print(f"Đã đọc file HTML: {html_file}")

        left_columns = soup.find('div', class_='left-columns')
        if left_columns:
            left_columns.append(BeautifulSoup(url_html, 'html.parser'))
            print(f"Đã thêm URL vào thẻ <div class='left-columns'>.")
        else:
            print("Không tìm thấy thẻ <div class='left-columns'> trong file HTML.")

        # Ghi lại file HTML sau khi thêm URL
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"Đã thêm URL thành công: {url}")
    except Exception as e:
        print(f"Lỗi khi thêm URL vào file HTML: {e}")


html_file = "nhung3.html"
articles = ScrapeDanTriTamLongNhanAi()
for article in articles:
    url = article.get("article_url", "No URL")
    print(f"Processing URL: {url}")
    if url and url != "No URL":
        add_url_to_website(html_file, url)
    else:
        print(f"Bỏ qua URL không hợp lệ: {url}")