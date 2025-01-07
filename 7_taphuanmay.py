from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import re

# Hàm tiền xử lý văn bản
def preprocess_text(text):
    """
    Hàm tiền xử lý văn bản: chuyển về chữ thường và loại bỏ các ký tự không cần thiết.
    """
    # Chuyển văn bản thành chữ thường
    text = text.lower()

    # Loại bỏ các ký tự không phải chữ cái tiếng Việt và khoảng trắng (bao gồm cả dấu tiếng Việt)
    text = re.sub(r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\s]', '', text)

    return text

# Hàm chuyển văn bản thành các vector số (TF-IDF)
def text_to_tfidf_vector(documents, vectorizer=None):
    """
    Hàm chuyển văn bản thành các vector số (TF-IDF)
    
    Args:
        documents (list of str): Danh sách các bài viết văn bản cần chuyển thành vector.
        vectorizer (TfidfVectorizer, optional): Một vectorizer đã được huấn luyện, nếu không sẽ tạo mới.
        
    Returns:
        tfidf_matrix (sparse matrix): Ma trận TF-IDF của các văn bản.
        vectorizer (TfidfVectorizer): Bộ vectorizer đã học từ dữ liệu.
    """
    # Tiền xử lý văn bản
    documents = [preprocess_text(doc) for doc in documents]

    # Nếu không có vectorizer, tạo một vectorizer mới và học từ dữ liệu
    if vectorizer is None:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
    else:
        # Nếu có vectorizer, chỉ sử dụng transform cho tập mới
        tfidf_matrix = vectorizer.transform(documents)

    return tfidf_matrix, vectorizer

# Dữ liệu mẫu
documents = [
    "Hỗ trợ các hoàn cảnh khó khăn luôn là một việc làm ý nghĩa.",
    "Chúng tôi đang tìm kiếm những người hảo tâm giúp đỡ trẻ em nghèo.",
    "Những hoàn cảnh gia đình gặp hoạn nạn cần sự hỗ trợ từ cộng đồng.",
    "Mọi đóng góp của các nhà hảo tâm sẽ giúp cải thiện cuộc sống của người nghèo.",
    "Trẻ em cần sự chăm sóc đặc biệt từ các tổ chức từ thiện.",
    "Chúng tôi sẽ giúp đỡ những gia đình gặp hoàn cảnh khó khăn.",
    "Mọi người cùng chung tay giúp đỡ trẻ em nghèo và gia đình khó khăn.",
    "Cộng đồng cùng nhau giúp đỡ những người cần sự trợ giúp."
]

# Nhãn phân loại cho các văn bản (0: Không cần hỗ trợ, 1: Cần hỗ trợ)
labels = [1, 1, 1, 1, 1, 1, 1, 1]  # Các bài viết đều liên quan đến hỗ trợ

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(documents, labels, test_size=0.25, random_state=42)

# Chuyển văn bản thành vector TF-IDF (chỉ fit trên tập huấn luyện)
X_train_tfidf, vectorizer = text_to_tfidf_vector(X_train)

# Chuyển tập kiểm tra thành vector TF-IDF sử dụng cùng một vectorizer
X_test_tfidf, _ = text_to_tfidf_vector(X_test, vectorizer)

# Khởi tạo và huấn luyện mô hình Naive Bayes
nb_model = MultinomialNB()
nb_model.fit(X_train_tfidf, y_train)

# Dự đoán trên tập kiểm tra
y_pred = nb_model.predict(X_test_tfidf)

# Đánh giá mô hình
accuracy = accuracy_score(y_test, y_pred)
print("Độ chính xác của mô hình: {:.2f}%".format(accuracy * 100))
print("\nBáo cáo phân loại:\n", classification_report(y_test, y_pred))