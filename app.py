from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import sqlite3
from bs4 import BeautifulSoup
import logging
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cần thiết để sử dụng flash messages

DB_FILE = 'dantri_articles.db'
HTML_FILE = 'nhung3.html'

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)

# Route để hiển thị trang chọn bài viết
@app.route('/', methods=['GET', 'POST'])
def select_articles():
    if request.method == 'POST':
        selected_ids = request.form.getlist('selected_articles')
        if selected_ids:
            transfer_result = transfer_articles(selected_ids)
            if isinstance(transfer_result, tuple):
                # Xử lý lỗi
                message, category = transfer_result
                flash(message, category)
            else:
                # Thành công
                flash(f"Đã chuyển {len(selected_ids)} bài viết thành công.", "success")
                return redirect(url_for('select_articles'))
        else:
            flash("Bạn chưa chọn bài viết nào để chuyển.", "warning")
    
    # Lấy các bài viết chưa được đăng
    articles = get_unpublished_articles(DB_FILE)
    
    # Debug: In ra các bài viết
    logging.debug("Articles to render:")
    for article in articles:
        logging.debug(article)
    
    return render_template('select_articles.html', articles=articles)

# API để lấy danh sách bài viết
@app.route('/get_articles', methods=['GET'])
def get_articles():
    articles = get_unpublished_articles(DB_FILE)
    articles_json = [
        {
            'id': article['id'],
            'title': article['title'],
            'summary': article['summary'],
            'predict': f"{article['predict']:.2f}",
            'url': article['url']
        } for article in articles
    ]
    return jsonify(articles_json)

# Hàm chuyển đổi các bài viết được chọn sang file HTML

def transfer_articles(selected_ids):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Để truy cập các cột bằng tên
        cursor = conn.cursor()

        # Truy vấn các bài viết được chọn
        placeholder = ','.join(['?'] * len(selected_ids))
        query = f"SELECT title, summary, predict, url FROM articles WHERE id IN ({placeholder})"
        cursor.execute(query, selected_ids)
        selected_articles = cursor.fetchall()

        if not selected_articles:
            return ("Không tìm thấy các bài viết được chọn trong cơ sở dữ liệu.", "error")

        # Đảm bảo rằng file HTML tồn tại với cấu trúc đúng
        if not os.path.exists(HTML_FILE):
            # Tạo cấu trúc cơ bản cho file HTML với thẻ <table>
            with open(HTML_FILE, 'w', encoding='utf-8') as file:
                file.write("""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Những Bài Viết Được Chuyển</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
        th { background-color: #f2f2f2; }
        a { color: blue; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Những Bài Viết Được Chuyển</h1>
    <table>
        <thead>
            <tr>
                <th>Tiêu đề</th>
                <th>Tóm tắt</th>
                <th>Predict</th>
                <th>URL</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
</body>
</html>
                """)

        # Sử dụng BeautifulSoup để chỉnh sửa file HTML
        with open(HTML_FILE, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Tìm thẻ <table>
        table = soup.find('table')
        if not table:
            logging.error("Không tìm thấy thẻ <table> trong nhung3.html.")
            return ("Không tìm thấy thẻ <table> trong nhung3.html.", "error")
        
        # Tìm thẻ <tbody>
        tbody = table.find('tbody')
        if not tbody:
            logging.debug("Không tìm thấy thẻ <tbody>. Tạo mới thẻ <tbody>.")
            tbody = soup.new_tag('tbody')
            table.append(tbody)

        # Thêm các bài viết được chọn vào <tbody>
        for article in selected_articles:
            title = article['title']
            summary = article['summary']
            predict = f"{article['predict']:.2f}"
            url = article['url']

            # Tạo một dòng mới trong bảng
            tr = soup.new_tag('tr')

            # Cột Tiêu đề
            td_title = soup.new_tag('td')
            td_title.string = title
            tr.append(td_title)

            # Cột Tóm tắt
            td_summary = soup.new_tag('td')
            td_summary.string = summary
            tr.append(td_summary)

            # Cột Predict
            td_predict = soup.new_tag('td')
            td_predict.string = predict
            tr.append(td_predict)

            # Cột URL
            td_url = soup.new_tag('td')
            a_tag = soup.new_tag('a', href=url, target='_blank')
            a_tag.string = "Xem bài viết"
            td_url.append(a_tag)
            tr.append(td_url)

            # Thêm dòng vào <tbody>
            tbody.append(tr)

        # Ghi lại nội dung đã chỉnh sửa vào file HTML
        with open(HTML_FILE, 'w', encoding='utf-8') as file:
            file.write(str(soup.prettify()))
        
        # Cập nhật trạng thái is_published trong cơ sở dữ liệu
        cursor.execute(f"UPDATE articles SET is_published = 1 WHERE id IN ({placeholder})", selected_ids)
        conn.commit()
        conn.close()

        logging.debug(f"Đã chuyển các bài viết: {selected_ids}")
        return "success"

    except Exception as e:
        logging.error(f"Lỗi khi chuyển bài viết: {e}")
        return (f"Lỗi khi chuyển bài viết: {e}", "error")
    
# Hàm lấy các bài viết chưa được đăng
def get_unpublished_articles(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Để truy cập các cột bằng tên
    cursor = conn.cursor()

    # Truy vấn các cột cụ thể
    cursor.execute("SELECT id, title, summary, predict, url FROM articles WHERE is_published = 0")
    articles = cursor.fetchall()
    conn.close()

    # Chuyển đổi các bài viết thành list của dict
    articles_list = []
    for article in articles:
        articles_list.append({
            'id': article['id'],
            'title': article['title'],
            'summary': article['summary'],
            'predict': article['predict'],
            'url': article['url']
        })
    return articles_list

if __name__ == '__main__':
    app.run(debug=True)