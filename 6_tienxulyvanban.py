from sklearn.feature_extraction.text import TfidfVectorizer 
import re

def preprocess_text(text):
    """
    Hàm tiền xử lý văn bản: chuyển về chữ thường và loại bỏ các ký tự không cần thiết.
    """
    # Chuyển văn bản thành chữ thường
    text = text.lower()

    # Loại bỏ các ký tự không phải chữ cái tiếng Việt và khoảng trắng (bao gồm cả dấu tiếng Việt)
    text = re.sub(r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\s]', '', text)

    return text

def text_to_tfidf_vector(documents):
    """
    Hàm chuyển văn bản thành các vector số (TF-IDF)
    
    Args:
        documents (list of str): Danh sách các bài viết văn bản cần chuyển thành vector.
        
    Returns:
        tfidf_matrix (sparse matrix): Ma trận TF-IDF của các văn bản.
        feature_names (list of str): Danh sách các từ trong từ điển (tính từ TF-IDF).
    """
    # Tiền xử lý văn bản
    documents = [preprocess_text(doc) for doc in documents]

    # Khởi tạo bộ vectorizer
    vectorizer = TfidfVectorizer()

    # Chuyển văn bản thành ma trận TF-IDF
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Lấy danh sách các từ đã học từ dữ liệu
    feature_names = vectorizer.get_feature_names_out()

    return tfidf_matrix, feature_names

# Ví dụ sử dụng thủ tục:
if __name__ == "__main__":
    # Một số bài viết mẫu
    documents = [
        "Hỗ trợ các hoàn cảnh khó khăn luôn là một việc làm ý nghĩa.",
        "Chúng tôi đang tìm kiếm những người hảo tâm giúp đỡ trẻ em nghèo.",
        "Những hoàn cảnh gia đình gặp hoạn nạn cần sự hỗ trợ từ cộng đồng.",
        "Mọi đóng góp của các nhà hảo tâm sẽ giúp cải thiện cuộc sống của người nghèo."
    ]
    
    # Chuyển văn bản thành TF-IDF vector
    tfidf_matrix, feature_names = text_to_tfidf_vector(documents)
    
    # In ra các từ trong từ điển
    print("Các từ trong từ điển:")
    print(feature_names)
    
    # In ra ma trận TF-IDF
    print("\nMa trận TF-IDF:")
    print(tfidf_matrix.toarray())  # Chuyển ma trận sparse thành array để dễ dàng xem kết quả