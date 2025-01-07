import requests
import os
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
        return "No Content", "No Image"

    print(f"Fetching article content from: {url}")
    soup = GetPageContentWithSelenium(url)
    if not soup:
        print(f"Failed to fetch article page: {url}")
        return "No Content", "No Image"

    # Lấy nội dung bài viết
    content_div = soup.find("div", class_="dt-news__body")
    if not content_div:
        print(f"No content found for article: {url}")
        return "No Content", "No Image"

    paragraphs = content_div.find_all("p")
    content = "\n".join([p.text.strip() for p in paragraphs])

    # Lấy URL hình ảnh
    image_tag = soup.find("img", class_="dt-news__content-img")
    image_url = image_tag['src'] if image_tag else "No Image"

    return content, image_url

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
        content, image_url = ScrapeArticleContent(article_url)
        print(f"Content length: {len(content)} characters")
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

# Ví dụ sử dụng
#html_file = "tam_long_nhan_ai.html"  # Tên file website trung gian
#articles = [
#    {"title": "Hơn 140 triệu đồng đến với người đàn bà đi cấy lúa thuê bị tai nạn",
#     "url": "https://dantri.com.vn/tam-long-nhan-ai/hon-140-trieu-dong-den-voi-nguoi-dan-ba-di-cay-lua-thue-bi-tai-nan-20241216093338091.htm",
#     "image_url": "https://cdnphoto.dantri.com.vn/vMHS9pXKJ8ccGiwtrKEje7ofxOk=/2024/12/16/1000108061-edited-1734315582596.jpeg"},
#    {"title": "Bạn đọc báo Dân trí giúp đỡ hoàn cảnh chồng mượn nhà làm lễ tang cho vợ",
#     "url": "https://dantri.com.vn/tam-long-nhan-ai/ban-doc-bao-dan-tri-giup-do-hoan-canh-chong-muon-nha-lam-le-tang-cho-vo-20241219091814215.htm",
#     "image_url": "https://cdnphoto.dantri.com.vn/BVw1XgYpK99hB1ijziUqJE6m8ns=/thumb_w/1020/2024/12/19/img6885-1734574460222.jpg?watermark=true"}
#]

articles = ScrapeDanTriTamLongNhanAi()
#for article in articles:
#    print(article)
#    send_to_main_website(article)
# Thêm từng bài viết vào file HTML
for article in articles:
    add_article_to_website(html_file, article["title"], article["url"], article["image_url"])