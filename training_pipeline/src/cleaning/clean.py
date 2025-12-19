import pandas as pd
from sklearn.model_selection import train_test_split
import re
from pathlib import Path

BASE_DIR = Path.cwd()
df = pd.read_csv(f"{BASE_DIR}/data/raw/banking_text.csv")  
def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'[^\w\s\d,?.!àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
    return " ".join(text.split())

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