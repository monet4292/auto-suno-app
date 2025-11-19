# Script tự động kích hoạt virtual environment cho dự án Suno Account Manager
# Sử dụng: .\activate.ps1

Write-Host "Đang kích hoạt virtual environment cho Suno Account Manager..." -ForegroundColor Green

# Kiểm tra xem virtual environment có tồn tại không
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    # Kích hoạt virtual environment
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment đã được kích hoạt!" -ForegroundColor Green
    Write-Host "Bây giờ bạn có thể chạy: python app.py" -ForegroundColor Yellow
} else {
    Write-Host "❌ Không tìm thấy virtual environment .venv" -ForegroundColor Red
    Write-Host "Vui lòng tạo virtual environment trước:" -ForegroundColor Yellow
    Write-Host "python -m venv .venv" -ForegroundColor Cyan
}

# Hiển thị thông tin môi trường
Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
Write-Host "Project path: $(Get-Location)" -ForegroundColor Cyan
