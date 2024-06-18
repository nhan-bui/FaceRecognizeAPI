# Bắt đầu từ một base image
FROM python:3.11-slim

# Cài đặt các công cụ cần thiết cho việc biên dịch
RUN apt-get update && apt-get install -y --fix-missing \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép tệp yêu cầu
COPY requirements.txt .

# Cài đặt các phụ thuộc Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép phần còn lại của mã ứng dụng
COPY . .

# Lệnh để chạy ứng dụng
EXPOSE 8080
