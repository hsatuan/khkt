from bs4 import BeautifulSoup

def filter_urls(input_file, output_file, filter_criteria=None):
    """
    Lọc các URL từ file nguồn (input_file) và thêm chúng vào file đích (output_file).
    
    Parameters:
        input_file (str): Đường dẫn đến file HTML nguồn.
        output_file (str): Đường dẫn đến file HTML đích.
        filter_criteria (function): Hàm để kiểm tra URL có hợp lệ không (trả về True/False).
    """
    try:
        # Đọc file nguồn
        with open(input_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Tìm tất cả các URL trong thẻ <div class="item">
        items = soup.find_all("div", class_="item")
        filtered_items = []

        for item in items:
            url = item.get("data-url")
            if url:
                # Kiểm tra điều kiện lọc
                if filter_criteria is None or filter_criteria(url):
                    filtered_items.append(item)

        # Đọc file đích hoặc tạo mới
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                output_soup = BeautifulSoup(f, 'html.parser')
        except FileNotFoundError:
            # Nếu file đích chưa tồn tại, tạo cấu trúc HTML cơ bản
            output_soup = BeautifulSoup("""
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="utf-8">
                <title>Dich</title>
            </head>
            <body>
                <div class="container">
                    <div class="left-columns"></div>
                </div>
            </body>
            </html>
            """, 'html.parser')

        # Thêm các mục đã lọc vào file đích
        left_columns = output_soup.find("div", class_="left-columns")
        for item in filtered_items:
            left_columns.append(item)

        # Ghi lại file đích
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(output_soup))

        print(f"Đã lọc và thêm {len(filtered_items)} URL vào file {output_file}.")
    except Exception as e:
        print(f"Lỗi trong quá trình lọc URL: {e}")

# Hàm kiểm tra URL có hợp lệ (ví dụ: chỉ chọn URL chứa "tam-long-nhan-ai")
def is_valid_url(url):
    return "tam-long-nhan-ai" in url

# Đường dẫn đến file nguồn và đích
input_file = "nhung3.html"
output_file = "dich.html"

# Lọc URL và ghi vào file đích
filter_urls(input_file, output_file, filter_criteria=is_valid_url)