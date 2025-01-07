import sqlite3 
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Hàm tiền xử lý văn bản
def preprocess_text(text):
    """
    Hàm tiền xử lý văn bản: chuyển về chữ thường và loại bỏ các ký tự không cần thiết.
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\s]', '', text)
    return text

# Hàm chuyển văn bản thành các vector số (TF-IDF)
def text_to_tfidf_vector(documents, vectorizer=None):
    """
    Hàm chuyển văn bản thành các vector số (TF-IDF)
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
#def update_predict(conn, article_id, predict_value):
    #cursor = conn.cursor()
    #cursor.execute("UPDATE articles SET is_published = ?  Predict = ? WHERE id = ?;", (0, predict_value, article_id))
    #conn.commit()
    #print(f"Đã cập nhật is_published, Predict cho bài viết ID {article_id}: {predict_value:.2f}")
    #cursor.close()

# Cập nhật giá trị Predict vào cơ sở dữ liệu
def update_predict(conn, article_id, predict_value):
    cursor = conn.cursor()
    predict_text = f"{predict_value:.4f}"  # Định dạng chuỗi 4 chữ số sau dấu phẩy
    cursor.execute(
        "UPDATE articles SET is_published = ?, Predict = ? WHERE id = ?;",
        (0, predict_text, article_id)
    )
    conn.commit()
    print(f"Đã cập nhật is_published, Predict cho bài viết ID {article_id}: {predict_value:.4f}")
    cursor.close()

# Huấn luyện mô hình
def train_model(documents, labels):
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        raise ValueError("Dữ liệu huấn luyện phải có ít nhất hai lớp (0 và 1).")

    X_train, X_test, y_train, y_test = train_test_split(documents, labels, test_size=0.25, random_state=42)
    X_train_tfidf, vectorizer = text_to_tfidf_vector(X_train)
    X_test_tfidf, _ = text_to_tfidf_vector(X_test, vectorizer)

    nb_model = MultinomialNB()
    nb_model.fit(X_train_tfidf, y_train)
    
    y_pred = nb_model.predict(X_test_tfidf)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

    return nb_model, vectorizer

def main():
    try:
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
        
        article_ids = [row[0] for row in articles]
        contents = [row[1] for row in articles]
        
        sample_documents = [
            "Hỗ trợ các hoàn cảnh khó khăn luôn là một việc làm ý nghĩa.",
            "Chúng tôi đang tìm kiếm những người hảo tâm giúp đỡ trẻ em nghèo.",
            "Những hoàn cảnh gia đình gặp hoạn nạn cần sự hỗ trợ từ cộng đồng.",
            "Mọi đóng góp của các nhà hảo tâm sẽ giúp cải thiện cuộc sống của người nghèo.",
            "Trẻ em cần sự chăm sóc đặc biệt từ các tổ chức từ thiện.",
            "Chúng tôi sẽ giúp đỡ những gia đình gặp hoàn cảnh khó khăn.",
            "Mọi người cùng chung tay giúp đỡ trẻ em nghèo và gia đình khó khăn.",
            "Cộng đồng cùng nhau giúp đỡ những người cần sự trợ giúp.",
            "Bài viết này không liên quan đến hỗ trợ.",
            "Không cần bất kỳ sự trợ giúp nào trong hoàn cảnh này.",
            "Mọi người tự giải quyết vấn đề của mình.",
            "Không có ai cần giúp đỡ trong tình huống này."
        ]
        sample_labels = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]  # Nhãn 1 và 0
        
        # Huấn luyện mô hình
        model, vectorizer = train_model(sample_documents, sample_labels)

        # Tiền xử lý và chuyển đổi nội dung bài viết cần dự đoán
        X_new_tfidf, _ = text_to_tfidf_vector(contents, vectorizer)

        # Dự đoán xác suất cần giúp đỡ
        probabilities = model.predict_proba(X_new_tfidf)[:, 1]

        # Cập nhật cơ sở dữ liệu với giá trị Predict
        for article_id, prob in zip(article_ids, probabilities):
            update_predict(conn, article_id, prob)
        
    except ValueError as ve:
        print("Lỗi:", ve)
    except Exception as e:
        print("Đã xảy ra lỗi:", e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
