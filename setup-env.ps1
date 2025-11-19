# Script thiết lập môi trường Python cho dự án Suno Account Manager
# Sử dụng: .\setup-env.ps1

param(
    [switch]$Force,  # Tham số để tạo lại virtual environment
    [switch]$SkipDeps # Bỏ qua việc cài đặt dependencies
)

Write-Host "=== Thiết lập môi trường cho Suno Account Manager ===" -ForegroundColor Cyan

# Kiểm tra Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python đã được cài đặt: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python không được cài đặt hoặc không có trong PATH" -ForegroundColor Red
    Write-Host "Vui lòng cài đặt Python 3.10+ từ https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Kiểm tra phiên bản Python
$versionParts = $pythonVersion -split ' '
$versionNumber = $versionParts[-1]
$majorVersion = [int]($versionNumber -split '\.')[0]

if ($majorVersion -lt 3) {
    Write-Host "❌ Cần Python 3.10 trở lên. Phiên bản hiện tại: $versionNumber" -ForegroundColor Red
    exit 1
}

# Tạo hoặc kiểm tra virtual environment
if ((Test-Path ".venv") -and -not $Force) {
    Write-Host "✅ Virtual environment .venv đã tồn tại" -ForegroundColor Green
} else {
    if ($Force) {
        Write-Host "🔄 Đang xóa virtual environment cũ..." -ForegroundColor Yellow
        Remove-Item -Path ".venv" -Recurse -Force
    }
    
    Write-Host "🔧 Đang tạo virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment đã được tạo thành công" -ForegroundColor Green
    } else {
        Write-Host "❌ Lỗi khi tạo virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Kích hoạt virtual environment
Write-Host "🔌 Đang kích hoạt virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Cài đặt dependencies
if (-not $SkipDeps) {
    if (Test-Path "requirements.txt") {
        Write-Host "📦 Đang cài đặt dependencies từ requirements.txt..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies đã được cài đặt thành công" -ForegroundColor Green
        } else {
            Write-Host "❌ Lỗi khi cài đặt dependencies" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "⚠️ Không tìm thấy file requirements.txt" -ForegroundColor Yellow
    }
}

# Hiển thị thông tin hoàn tất
Write-Host "=== Hoàn tất! ===" -ForegroundColor Green
Write-Host "Virtual environment đã sẵn sàng để sử dụng." -ForegroundColor Green
Write-Host "Để chạy ứng dụng: python app.py" -ForegroundColor Cyan
Write-Host "Để thoát virtual environment: deactivate" -ForegroundColor Cyan

# Tạo shortcut script cho lần sau
if (-not (Test-Path "activate.ps1")) {
    Write-Host "📝 Đang tạo script kích hoạt nhanh (activate.ps1)..." -ForegroundColor Yellow
    @"
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
    Write-Host "Vui lòng chạy: .\setup-env.ps1" -ForegroundColor Yellow
}
"@ | Out-File -FilePath "activate.ps1" -Encoding UTF8
    Write-Host "✅ Đã tạo script activate.ps1 cho lần sau" -ForegroundColor Green
}
