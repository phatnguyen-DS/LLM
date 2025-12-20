"""
Hệ thống Phân loại Văn bản Tiếng Việt - Module Xử lý Dữ liệu
File: clean.py
Mô tả: Làm sạch và chuẩn hóa văn bản tiếng Việt
Tác giả: TAN PHAT
Chức năng: Làm sạch văn bản, loại bỏ ký tự đặc biệt, chuẩn hóa Unicode, và chia dữ liệu
"""

import pandas as pd
from sklearn.model_selection import train_test_split
import re
from pathlib import Path

# ======== CẤU HÌNH TOÀN CỤC ===
BASE_DIR = Path.cwd()

# Đọc dữ liệu thô
try:
    print("[INFO] Đang đọc dữ liệu từ:", f"{BASE_DIR}/data/raw/banking_text.csv")
    df = pd.read_csv(f"{BASE_DIR}/data/raw/banking_text.csv")
    print(f"[INFO] Đã đọc thành công, {len(df)} dòng dữ liệu")
except Exception as e:
    print(f"[ERROR] Không thể đọc dữ liệu: {e}")
    raise e

# ======== HÀM XỬ LÝ DẠT ===
def clean_text(text):
    """
    Làm sạch văn bản tiếng Việt:
    - Loại bỏ ký tự đặc biệt, giữ lại ký tự có nghĩa
    - Chuẩn hóa về chữ thường
    - Loại bỏ khoảng trắng thừa
    """
    if not isinstance(text, str): 
        return ""
    
    # Loại bỏ các ký tự đặc biệt, chỉ giữ lại ký tự Latin, số, và ký tự tiếng Việt
    text = re.sub(r'[^\w\s\d,?.!àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
    
    # Chuẩn hóa về chữ thường
    text = text.lower()
    
    # Loại bỏ khoảng trắng thừa
    text = " ".join(text.split())
    
    return text

# ======== XỬ LÝ DỮ GIẢM ===
# Loại bỏ các dòng trống
df = df.dropna(subset=['text'])

# Áp dụng hàm làm sạch
df['text_clean'] = df['text'].apply(clean_text)

# Loại bỏ các văn bản quá ngắn
df = df[df['text_clean'].str.len() > 3]

# Loại bỏ các bản trùng lặp
df = df.drop_duplicates(subset=['text_clean'])

# ======== ÁNH DÁNH LABEL ===
label_map = {
    "CARD_ISSUE": 0, "APP_LOGIN": 1, "TRANSACTION": 2,
    "LOAN_SAVING": 3, "FRAUD_REPORT": 4, "OTHERS": 5
}

# Chuyển đổi text thành số
df['label_id'] = df['label'].map(label_map)

print(f"[INFO] Đã làm sạch dữ liệu, còn {len(df)} dòng")

# ======== CHIA DỮ LIỆU (TRAIN/VAL/TEST SPLIT) ===
try:
    # Chia dữ liệu: 80% train, 10% val, 10% test
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label_id'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label_id'])
    
    print(f"[INFO] Đã chia dữ liệu:")
    print(f"  - Train: {len(train_df)} dòng")
    print(f"  - Validation: {len(val_df)} dòng")
    print(f"  - Test: {len(test_df)} dòng")
    
except Exception as e:
    print(f"[ERROR] Lỗi khi chia dữ liệu: {e}")
    raise e

# ======== LƯU DỮ GIẢM ===
try:
    output_dir = BASE_DIR / "data/processed"
    output_dir.mkdir(exist_ok=True)
    print(f"[INFO] Tạo thư mục output tại: {output_dir}")
    
    # Lưu các file đã xử lý
    train_df.to_csv(output_dir / "train.csv", index=False)
    val_df.to_csv(output_dir / "val.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)
    
    print("[INFO] Đã lưu dữ liệu đã xử lý vào:")
    print(f"  - Train: {output_dir / 'train.csv'}")
    print(f"  - Validation: {output_dir / 'val.csv'}")
    print(f"  - Test: {output_dir / 'test.csv'}")
    
except Exception as e:
    print(f"[ERROR] Lỗi khi lưu dữ liệu: {e}")
    raise e

print("[SUCCESS] Hoàn thành quá trình làm sạch và chuẩn hóa dữ liệu!")

df['text_clean'] = df['text'].apply(clean_text)
df = df[df['text_clean'].str.len() > 3]
df = df.drop_duplicates(subset=['text_clean'])
label_map = {
    "CARD_ISSUE": 0, "APP_LOGIN": 1, "TRANSACTION": 2,
    "LOAN_SAVING": 3, "FRAUD_REPORT": 4, "OTHERS": 5
}
df['label_id'] = df['label'].map(label_map)

train_df, test_val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label_id'])
val_df, test_df = train_test_split(test_val_df, test_size=0.5, random_state=42, stratify=test_val_df['label_id'])

train_df.to_csv(BASE_DIR / "data/processed/train.csv", index=False)
val_df.to_csv(BASE_DIR / "data/processed/val.csv", index=False)
test_df.to_csv(BASE_DIR / "data/processed/test.csv", index=False)
