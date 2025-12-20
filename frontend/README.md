# Frontend - Giao diện Phân loại Văn bản

## Tổng quan

Frontend của dự án được xây dựng bằng HTML, CSS và JavaScript thuần túy, không sử dụng framework nặng. Thiết kế chuyên nghiệp, hiện đại và phù hợp với môi trường doanh nghiệp.

## Các tính năng chính

- **Giao diện hiện đại**: Sử dụng Bootstrap 5 với thiết kế responsive
- **Hiệu ứng mượt mà**: Animation và transition tinh tế
- **Tương tác trực tiếp**: Gọi API backend một cách liền mạch
- **Trạng thái thời gian thực**: Hiển thị trạng thái API
- **Ví dụ mẫu**: Cung cấp các ví dụ văn bản để thử nghiệm
- **Xử lý lỗi thân thiện**: Hiển thị thông báo lỗi rõ ràng

## Cấu trúc thư mục

```
frontend/
├── index.html          # File HTML chính
├── styles.css          # File CSS tùy chỉnh
├── script.js           # File JavaScript xử lý tương tác
├── nginx.conf          # Cấu hình Nginx cho production
├── Dockerfile          # Dockerfile để build image
└── README.md          # Tài liệu này
```

## Thiết kế UI/UX

### Màu sắc
- **Primary**: #4361ee (Xanh dương chuyên nghiệp)
- **Secondary**: #64748b (Xám xám)
- **Success**: #10b981 (Xanh lá)
- **Danger**: #ef4444 (Đỏ)
- **Warning**: #f59e0b (Vàng)
- **Info**: #3b82f6 (Xanh dương nhạt)

### Font chữ
- Inter: Font chữ hiện đại, dễ đọc
- Kích thước: 16px base font
- Độ đậm: 300-700

### Responsive
- Desktop: 100% width
- Tablet: Tối ưu cho 768px
- Mobile: Tối ưu cho 480px

## Triển khai

### Local Development

```bash
# Chạy nginx local với file cấu hình
nginx -c $(pwd)/nginx.conf

# Hoặc sử dụng Python simple server
python -m http.server 8080
```

### Docker Deployment

```bash
# Build image
docker build -f frontend/Dockerfile -t text-classification-frontend .

# Chạy container
docker run -p 80:80 text-classification-frontend
```

### Render Deployment

1. Build image và push lên registry
2. Kết nối repository với Render
3. Cấu hình Web Service
4. Thiết lập port: 80

## Tùy chỉnh API

Thay đổi URL API trong file `script.js`:

```javascript
const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

## Tối ưu hóa

- **Gzip compression**: Tự động nén các file tĩnh
- **Static file caching**: Lưu cache các file CSS, JS, hình ảnh
- **Security headers**: Bảo vệ ứng dụng khỏi các lỗ hổng phổ biến
- **Small image size**: Dùng Nginx Alpine (dưới 50MB)

## Tương thích trình duyệt

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Định dạng kết quả API

```json
{
    "label": "CARD_ISSUE",
    "score": 0.9342
}
```

## Hướng dẫn sử dụng

1. Mở trang web
2. Nhập văn bản cần phân loại (tối thiểu 10 ký tự)
3. Nhấn nút "Phân loại"
4. Xem kết quả với độ tin cậy

## Các lớp phân loại

- **CARD_ISSUE**: Vấn đề liên quan đến thẻ
- **APP_LOGIN**: Vấn đề đăng nhập ứng dụng
- **TRANSACTION**: Vấn đề giao dịch
- **LOAN_SAVING**: Vấn đề vay/tiết kiệm
- **FRAUD_REPORT**: Báo cáo lừa đảo
- **OTHERS**: Các vấn đề khác
