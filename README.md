# Instagram Account Checker

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/600px-Instagram_icon.png" width="100" height="100" alt="Instagram Logo">
</p>

<p align="center">
  <b>Công cụ kiểm tra trạng thái tài khoản Instagram</b><br>
  <i>Developed by <a href="https://t.me/HoangAnhDev">HoangAnhDev</a></i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0-red.svg" alt="Version">
</p>

## 📋 Tính năng

- ✅ Kiểm tra hàng loạt tài khoản Instagram từ file
- ✅ Phân loại tài khoản thành LIVE, DIE và UNKNOWN
- ✅ Hỗ trợ sử dụng proxy (HTTP và SOCKS5)
- ✅ Tự động phát hiện loại proxy (SOCKS5 hoặc HTTP)
- ✅ Nhiều phương thức API để kiểm tra tài khoản
- ✅ Hiển thị thống kê trực quan với màu sắc
- ✅ Nhiều tùy chọn tốc độ kiểm tra
- ✅ Chế độ debug để theo dõi chi tiết

## 🔧 Yêu cầu

- Python 3.6 trở lên
- Các thư viện: `requests`, `colorama`, `tabulate`

## 📥 Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/HoangAnhDev/instagram-account-checker.git
cd instagram-account-checker
```

### Bước 2: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

## 🚀 Cách sử dụng

### Chuẩn bị file dữ liệu

1. Tạo file `account.txt` với mỗi dòng là một tài khoản theo định dạng:

   ```
   username|password|...
   ```

   (Chỉ cần username ở đầu mỗi dòng, các thông tin khác không ảnh hưởng đến việc kiểm tra)

2. (Tùy chọn) Tạo file `proxy.txt` với mỗi dòng là một proxy theo định dạng:
   ```
   ip:port
   hoặc
   http://ip:port
   hoặc
   socks5://ip:port
   ```

### Chạy tool

```bash
python check_accounts.py
```

### Các tùy chọn khi chạy tool

1. **Chế độ debug**: Hiển thị thông tin chi tiết về quá trình kiểm tra

   ```
   Bật chế độ debug? (y/n): y
   ```

2. **Tốc độ kiểm tra**:

   ```
   Chọn tốc độ kiểm tra:
   1. Chậm (an toàn nhất, ít bị chặn)
   2. Trung bình
   3. Nhanh (có thể bị chặn IP)
   ```

3. **Phương thức API ưu tiên**:
   ```
   Chọn phương thức API ưu tiên:
   0. Tự động (thử tất cả các phương thức)
   1. API Web (?__a=1&__d=dis)
   2. API Mobile (web_profile_info)
   3. Kiểm tra trực tiếp trang profile
   ```

### Kết quả

Kết quả kiểm tra sẽ được lưu vào các file:

- `LIVE.txt`: Các tài khoản còn sống
- `DIE.txt`: Các tài khoản đã chết
- `UNKNOWN.txt`: Các tài khoản không xác định được trạng thái

## 📊 Hiển thị kết quả

Tool sẽ hiển thị bảng thống kê trong quá trình kiểm tra:

```
+------------+-----------+
| Trạng thái | Số lượng  |
+============+===========+
| Tổng       | 100       |
+------------+-----------+
| LIVE       | 60        |
+------------+-----------+
| DIE        | 30        |
+------------+-----------+
| Tỉ lệ      | 60.00%    |
+------------+-----------+

Đã kiểm tra: 90/100
UNKNOWN: 0
Tốc độ: Trung bình
Phương thức API: Tự động
```

## 🔍 Các phương thức API

Tool sử dụng 3 phương thức API khác nhau để kiểm tra tài khoản Instagram:

1. **API Web (?**a=1&**d=dis)**:

   - Endpoint: `https://www.instagram.com/{username}/?__a=1&__d=dis`
   - Ưu điểm: Cung cấp nhiều thông tin chi tiết
   - Nhược điểm: Có thể bị chặn sau nhiều request

2. **API Mobile (web_profile_info)**:

   - Endpoint: `https://i.instagram.com/api/v1/users/web_profile_info/?username={username}`
   - Ưu điểm: Ít bị chặn hơn API Web
   - Nhược điểm: Yêu cầu thêm header đặc biệt

3. **Kiểm tra trực tiếp trang profile**:
   - Endpoint: `https://www.instagram.com/{username}/`
   - Ưu điểm: Ít bị chặn nhất
   - Nhược điểm: Ít thông tin chi tiết hơn

## 🚫 Lưu ý

- Tool này sử dụng API không chính thức của Instagram, có thể bị thay đổi hoặc chặn bởi Instagram bất cứ lúc nào.
- Sử dụng quá nhiều request có thể dẫn đến việc bị chặn IP.
- Nên sử dụng proxy để tránh bị chặn IP.
- Tool này chỉ dùng cho mục đích học tập và nghiên cứu.

## 📝 Các lệnh hữu ích

### Kiểm tra tài khoản đơn lẻ

```bash
python check_instagram.py
```

### Kiểm tra hàng loạt tài khoản từ file

```bash
python check_accounts.py
```

### Cài đặt thư viện cần thiết

```bash
pip install requests colorama tabulate
```

## 📞 Liên hệ

- **Telegram**: [@HoangAnhDev](https://t.me/HoangAnhDev)
- **GitHub**: [HoangAnhDev](https://github.com/HoangAnhDev)

## 📜 Giấy phép

MIT License

Copyright (c) 2023 HoangAnhDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
