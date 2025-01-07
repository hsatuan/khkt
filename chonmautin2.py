import sqlite3
from bs4 import BeautifulSoup

def generate_nhung3_html(db_path, output_html):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT url, title, image_url FROM urls WHERE selected = 1")
        selected_urls = cursor.fetchall()

        # Tạo soup mới cho file đích (nhung3.html)
        soup = BeautifulSoup("<!DOCTYPE html>\n<html lang=\"vi\"></html>", 'html.parser')
        head_tag = soup.new_tag("head")
        body_tag = soup.new_tag("body")
        soup.append(head_tag)
        soup.append(body_tag)

        # Đọc nội dung từ nhung3_chebo.html
        try:
            with open('nhung3_chebo.html', 'r', encoding='utf-8') as f:
                soup_chebo = BeautifulSoup(f, 'html.parser')
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file nhung3_chebo.html")
            return
        except Exception as e:
            print(f"Lỗi khi đọc file nhung3_chebo.html: {e}")
            return


        # Sao chép head (nếu có)
        if soup_chebo.head:
            soup.head.extend(soup_chebo.head.contents) # Sử dụng extend để sao chép nội dung

        # Sao chép header (nếu có)
        if soup_chebo.header:
            soup.body.append(soup_chebo.header.extract()) # extract để di chuyển chứ không phải copy

        # Tạo container và left-columns
        container = soup.new_tag('div', class_='container')
        left_columns = soup.new_tag('div', class_='left-columns')
        container.append(left_columns)
        soup.body.append(container)

        # Sao chép right-column (nếu có)
        right_column = soup_chebo.find('div', class_='right-column')
        if right_column:
            container.append(right_column.extract())

        # Sao chép footer (nếu có)
        if soup_chebo.footer:
            soup.body.append(soup_chebo.footer.extract())# extract để di chuyển chứ không phải copy
        else:
            print("Không tìm thấy footer!")
            footer = soup.new_tag("footer")
            footer.string = "© 2024 Tấm Lòng Nhân Ái" # Tạo footer mặc định
            soup.body.append(footer)

        for url, title, image_url in selected_urls:
            # ... (phần code tạo item như cũ)
            item = soup.new_tag('div', class_='item', attrs={'data-url': url})
            if image_url:
                img = soup.new_tag('img', alt=title, src=image_url)
                item.append(img)
            a = soup.new_tag('a', href=url)
            a.string = title
            item.append(a)
            left_columns.append(item)

        try:
            with open(output_html, 'w', encoding='utf-8') as outfile:
                outfile.write(str(soup.prettify())) # Sử dụng prettify để format HTML
            print(f"Selected items saved to '{output_html}' successfully.")
        except Exception as e:
            print(f"Error writing to target file: {e}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Ví dụ sử dụng:
db_path = 'urls.db'
output_html = 'nhung3.html'
generate_nhung3_html(db_path, output_html)