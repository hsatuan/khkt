import requests
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

added_urls = set()

def load_added_urls(html_file):
    """Load các URL đã có trong file HTML vào danh sách."""
    if not os.path.exists(html_file):
        return set()

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Lấy danh sách các URL từ các thẻ <div class="item" data-url="">
    return {item['data-url'] for item in soup.find_all('div', class_='item') if item.get('data-url')}

html_file = "nhung3.html"
def add_article_to_website(html_file, title, url, image_url):
    """Thêm bài viết vào website trung gian nếu chưa tồn tại."""
    global added_urls

    if url in added_urls:
        print(f"URL đã tồn tại, bỏ qua: {url}")
        return

    # Thẻ <div> mới cho bài viết
    article_html = f"""
    <div class="item" data-url="{url}">
        <img src="{image_url}" alt="{title}">
        <a href="{url}" target="_blank">{title}</a>
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
        return

    # Ghi lại nội dung HTML đã cập nhật
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Đã thêm bài viết: {title}")

    # Thêm URL vào danh sách đã thêm
    added_urls.add(url)

# Load các URL đã có trong file HTML
added_urls = load_added_urls(html_file)

# Thêm từng bài viết vào file HTML
for article in articles:
    add_article_to_website(html_file, article["title"], article["article_url"], article["image_url"])

#articles = ScrapeDanTriTamLongNhanAi()
#for article in articles:
#    print(article)
#    send_to_main_website(article)
# Thêm từng bài viết vào file HTML
#for article in articles:
#    add_article_to_website(html_file, article["title"], article["url"], article["image_url"])