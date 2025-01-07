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
    cursor = conn.cursor()

    if request.method == 'POST':
        selected_urls = request.form.getlist('selected_articles')
        if selected_urls:
            # Cập nhật trạng thái is_published trong cơ sở dữ liệu
            mark_articles_as_published(DB_FILE, selected_urls)
    # Truy vấn các bài viết chưa được đăng
    articles = get_unpublished_articles(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT url, title, image_url FROM articles WHERE id IN ({','.join('?' for _ in selected_ids)})", selected_ids)
    selected_articles = cursor.fetchall()
    conn.close()

    # Update nhung3.html
    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    left_columns = soup.find('div', class_='left-columns')
    if not left_columns:
        return "Không tìm thấy thẻ <div class='left-columns'> trong nhung3.html", 400

    for url, title, image_url in selected_articles:
        new_div = soup.new_tag('div', **{'class': 'item', 'data-url': url})
        new_img = soup.new_tag('img', src=image_url, alt=title)
        new_a = soup.new_tag('a', href=url, target='_blank')
        new_a.string = title or 'No Title'
        new_div.append(new_img)
        new_div.append(new_a)
        left_columns.append(new_div)

    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(str(soup))

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
    print("Route /publish được gọi")  # Log để kiểm tra
    selected_urls = request.form.getlist('selected_articles')  # Lấy danh sách URL từ form
    print(f"Selected URLs: {selected_urls}")  # Log để kiểm tra

    if not selected_urls:
        return "Không có bài viết nào được chọn để xuất bản.", 400

    # Kết nối cơ sở dữ liệu
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Mở file nhung3.html để thêm bài viết
    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Lấy thẻ <div class="left-columns">
    left_columns = soup.find('div', class_='left-columns')
    if not left_columns:
        return "Không tìm thấy thẻ <div class='left-columns'> trong file nhung3.html", 500

    # Thêm bài viết vào HTML và cập nhật trạng thái is_published
    for url in selected_urls:
        cursor.execute("SELECT url, title, summary FROM articles WHERE url = ?", (url,))
        article = cursor.fetchone()

        if article:
            article_url, article_title, article_summary = article

            # Tạo thẻ HTML mới
            new_item = soup.new_tag('div', **{'class': 'item', 'data-url': article_url})
            new_item.append(BeautifulSoup(f'<a href="{article_url}" target="_blank">{article_title}</a>', 'html.parser'))
            left_columns.append(new_item)

            # Cập nhật trạng thái is_published
            cursor.execute("UPDATE articles SET is_published = 1 WHERE url = ?", (article_url,))

       # Lưu lại file nhung3.html
    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    # Lưu thay đổi vào cơ sở dữ liệu
    conn.commit()
    conn.close()

    return "Các bài viết đã được xuất bản thành công!"

def get_unpublished_articles(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Lấy các bài viết chưa được đăng
    cursor.execute("SELECT * FROM articles WHERE is_published = 0")
    articles = cursor.fetchall()
    conn.close()
    return articles

if __name__ == '__main__':
    app.run(debug=True)

