@echo off
REM Script tự động kích hoạt virtual environment cho dự án Suno Account Manager
REM Sử dụng: activate.bat

echo Đang kích hoạt virtual environment cho Suno Account Manager...

REM Kiểm tra xem virtual environment có tồn tại không
if exist ".venv\Scripts\activate.bat" (
    REM Kích hoạt virtual environment
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment đã được kích hoạt!
    echo Bây giờ bạn có thể chạy: python app.py
) else (
    echo ❌ Không tìm thấy virtual environment .venv
    echo Vui lòng tạo virtual environment trước:
    echo python -m venv .venv
)

REM Hiển thị thông tin môi trường
echo Python version:
python --version
echo Project path: %CD%
