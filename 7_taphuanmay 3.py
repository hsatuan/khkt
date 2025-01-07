import sqlite3
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Hàm tiền xử lý văn bản
def preprocess_text(text):
    """
    Chuyển văn bản thành chữ thường và loại bỏ các ký tự không cần thiết.
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\s]', '', text)
    return text

# Hàm chuyển văn bản thành các vector số (TF-IDF)
def text_to_tfidf_vector(documents, vectorizer=None):
    """
    Chuyển văn bản thành vector TF-IDF.
    """
    documents = [preprocess_text(doc) for doc in documents]
    if vectorizer is None:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
    else:
        tfidf_matrix = vectorizer.transform(documents)
    return tfidf_matrix, vectorizer

# Kết nối đến cơ sở dữ liệu SQLite
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Thêm cột Predict nếu chưa tồn tại
def add_predict_column(conn):
    cursor = conn.cursor()
    # Kiểm tra xem cột Predict đã tồn tại chưa
    cursor.execute("PRAGMA table_info(articles);")
    columns = [info[1] for info in cursor.fetchall()]
    if 'Predict' not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN Predict REAL;")
        conn.commit()
    cursor.close()

# Lấy các bài viết cần dự đoán (Predict còn NULL)
def fetch_articles_to_predict(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM articles WHERE Predict IS NULL;")
    rows = cursor.fetchall()
    cursor.close()
    return rows  # Danh sách các tuple (id, content)

# Cập nhật giá trị Predict vào cơ sở dữ liệu
def update_predict(conn, article_id, predict_value):
    cursor = conn.cursor()
    cursor.execute("UPDATE articles SET Predict = ? WHERE id = ?;", (predict_value, article_id))
    conn.commit()
    cursor.close()

# Huấn luyện mô hình
def train_model(documents, labels):
    # Kiểm tra số lượng lớp
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        raise ValueError("Dữ liệu huấn luyện phải có ít nhất hai lớp (0 và 1).")

    # Chia dữ liệu thành tập huấn luyện và kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(documents, labels, test_size=0.25, random_state=42)
    
    # Chuyển văn bản thành vector TF-IDF (fit trên tập huấn luyện)
    X_train_tfidf, vectorizer = text_to_tfidf_vector(X_train)
    
    # Chuyển tập kiểm tra thành vector TF-IDF sử dụng cùng một vectorizer
    X_test_tfidf, _ = text_to_tfidf_vector(X_test, vectorizer)
    
    # Khởi tạo và huấn luyện mô hình Naive Bayes
    nb_model = MultinomialNB()
    nb_model.fit(X_train_tfidf, y_train)
    
    # Đánh giá mô hình trên tập kiểm tra
    y_pred = nb_model.predict(X_test_tfidf)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))
    
    return nb_model, vectorizer

def main():
    try:
        # Kết nối đến cơ sở dữ liệu
        db_path = 'dantri_articles.db'
        conn = connect_db(db_path)
        
        # Thêm cột Predict nếu chưa tồn tại
        add_predict_column(conn)
        
        # Lấy các bài viết cần dự đoán
        articles = fetch_articles_to_predict(conn)
        if not articles:
            print("Không có bài viết nào cần dự đoán.")
            conn.close()
            return
        
        # Tách id và nội dung
        article_ids = [row[0] for row in articles]
        contents = [row[1] for row in articles]
        
        # Dữ liệu mẫu để huấn luyện mô hình
        sample_documents = [
            "Hỗ trợ các hoàn cảnh khó khăn luôn là một việc làm ý nghĩa.",
            "Chúng tôi đang tìm kiếm những người hảo tâm giúp đỡ trẻ em nghèo.",
            "Những hoàn cảnh gia đình gặp hoạn nạn cần sự hỗ trợ từ cộng đồng.",
            "Mọi đóng góp của các nhà hảo tâm sẽ giúp cải thiện cuộc sống của người nghèo.",
            "Trẻ em cần sự chăm sóc đặc biệt từ các tổ chức từ thiện.",
            "Chúng tôi sẽ giúp đỡ những gia đình gặp hoàn cảnh khó khăn.",
            "Mọi người cùng chung tay giúp đỡ trẻ em nghèo và gia đình khó khăn.",
            "Cộng đồng cùng nhau giúp đỡ những người cần sự trợ giúp.",
            "Bài viết này không liên quan đến hỗ trợ.",  # Nhãn 0
            "Không cần bất kỳ sự trợ giúp nào trong hoàn cảnh này.",  # Nhãn 0
            "Mọi người tự giải quyết vấn đề của mình.",  # Nhãn 0
            "Không có ai cần giúp đỡ trong tình huống này."  # Nhãn 0
        ]
        sample_labels = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]  # Bao gồm cả nhãn 0 và 1
        
        # Huấn luyện mô hình
        model, vectorizer = train_model(sample_documents, sample_labels)
        
        # Tiền xử lý và chuyển đổi nội dung bài viết cần dự đoán
        X_new_tfidf, _ = text_to_tfidf_vector(contents, vectorizer)
        
        # Dự đoán xác suất cần giúp đỡ (probability for class 1)
        probabilities = model.predict_proba(X_new_tfidf)[:, 1]  # Lấy cột xác suất cho class 1
        
        # Cập nhật cơ sở dữ liệu với giá trị Predict
        for article_id, prob in zip(article_ids, probabilities):
            update_predict(conn, article_id, prob)
            print(f"Đã cập nhật Predict cho bài viết ID {article_id}: {prob:.2f}")
        
    except ValueError as ve:
        print("Lỗi:", ve)
    except Exception as e:
        print("Đã xảy ra lỗi:", e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()