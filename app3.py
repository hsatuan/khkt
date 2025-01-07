from flask import Flask, jsonify, request, render_template
import sqlite3
from bs4 import BeautifulSoup
import logging
app = Flask(__name__)
DB_FILE = 'dantri_articles.db'
HTML_FILE = 'nhung3.html'
# Route to render the selection page

@app.route('/', methods=['GET', 'POST'])
def select_articles():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_urls = request.form.getlist('selected_articles')
        if selected_urls:
            mark_articles_as_published(DB_FILE, selected_urls)
    
    articles = get_unpublished_articles(DB_FILE)

    # In dữ liệu ra để debug
    #for article in articles:
    #    print(dict(article))

    conn.close()
    return render_template('select_articles.html', articles=articles)

# API to get articles from database
@app.route('/get_articles', methods=['GET'])
def get_articles():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, title FROM articles")
    articles = [{'id': row[0], 'url': row[1], 'title': row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(articles)

# API to save selected articles to nhung3.html
@app.route('/save_selection', methods=['POST'])
def save_selection():
    selected_ids = request.json.get('selected', [])
    if not selected_ids:
        return "Không có bài viết nào được chọn.", 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Lấy thông tin bài viết được chọn từ cơ sở dữ liệu
    cursor.execute(f"SELECT id, url, title, content, image_url FROM articles WHERE id IN ({','.join('?' for _ in selected_ids)})", selected_ids)
    selected_articles = cursor.fetchall()

    # Đọc nội dung file HTML nhung3.html
    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Tìm thẻ <div class="left-columns">
    left_columns = soup.find('div', class_='left-columns')
    if not left_columns:
        return "Không tìm thấy thẻ <div class='left-columns'> trong file nhung3.html", 500

    # Thêm bài viết vào left-columns
    for article_id, url, title, content, image_url in selected_articles:
        # Tạo một div mới cho bài viết
        new_div = soup.new_tag('div', **{'class': 'item', 'data-url': url})

        # Thêm hình ảnh nếu có
        if image_url:
            new_img = soup.new_tag('img', src=image_url, alt=title or 'No Title')
            new_div.append(new_img)

        # Thêm liên kết tiêu đề
        new_a = soup.new_tag('a', href=url, target='_blank')
        new_a.string = title or 'No Title'
        new_div.append(new_a)

        # Thêm nội dung bài viết
        #if content:
        #    new_content = soup.new_tag('p')
        #    new_content.string = content
        #    new_div.append(new_content)

        # Thêm div mới vào left-columns
        left_columns.append(new_div)

        # Cập nhật trạng thái bài viết trong cơ sở dữ liệu
        cursor.execute("UPDATE articles SET is_published = 1 WHERE id = ?", (article_id,))

    # Ghi lại nội dung vào file nhung3.html
    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    # Lưu thay đổi vào cơ sở dữ liệu
    conn.commit()
    conn.close()

    return "Bài viết đã được chuyển thành công.", 200

def mark_articles_as_published(DB_FILE, selected_urls):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for url in selected_urls:
        cursor.execute("UPDATE articles SET is_published = 1 WHERE url = ?", (url,))
    
    conn.commit()
    print("Đã cập nhật trạng thái bài viết là đã đăng.")
    conn.close()

logging.basicConfig(level=logging.DEBUG)
@app.route('/publish', methods=['POST'])
def publish_articles():
    logging.debug("Route /publish was called")
    selected_urls = request.form.getlist('selected_articles')
    if not selected_urls:
        return "Không có bài viết nào được chọn để xuất bản.", 400

    nhung3_file = 'nhung3.html'
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Thêm dòng này
    cursor = conn.cursor()

    with open(nhung3_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    left_columns = soup.find('div', class_='left-columns')
    if not left_columns:
        return "Không tìm thấy thẻ <div class='left-columns'> trong file nhung3.html", 500

    for url in selected_urls:
        cursor.execute("SELECT url, title, image_url FROM articles WHERE url = ?", (url,))
        article = cursor.fetchone()
        if article:
            article_url = article['url']
            article_title = article['title']
            image_url = article['image_url']
            
            new_div = soup.new_tag('div', **{'class': 'item', 'data-url': url})
            new_img = soup.new_tag('img', src=image_url, alt=article_title)
            new_a = soup.new_tag('a', href=url, target='_blank')
            new_a.string = article_title or 'No Title'
            new_div.append(new_img)
            new_div.append(new_a)
            left_columns.append(new_div)
            cursor.execute("UPDATE articles SET is_published = 1 WHERE url = ?", (article_url,))

    with open(nhung3_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    conn.commit()
    conn.close()
    logging.debug(f"Published articles: {selected_urls}")

    return "Các bài viết đã được xuất bản thành công!"

def get_unpublished_articles(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, url, summary, predict, some_number_field FROM articles WHERE is_published = 0")
    rows = cursor.fetchall()

    articles = []
    for row in rows:
        article = dict(row)
        # Định dạng predict với 2 chữ số thập phân
        if 'predict' in article and article['predict'] is not None:
            article['predict'] = round(float(article['predict']), 2)
        articles.append(article)

    conn.close()
    return articles

if __name__ == '__main__':
    app.run(debug=True)

