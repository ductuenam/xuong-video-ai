# Bộ cài Xưởng Video AI cho Windows. Chạy trong thư mục Bộ Não AI (Claude mở đúng thư mục đó):
#   powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"
# Chạy lại cùng lệnh = cập nhật. Không cần quyền quản trị, không cần Git, winget.
# Việc của tệp này: tải uv (trình quản lý Python), cài Python 3.12 riêng cho xưởng, tải mã xưởng, rồi chạy cai_xuong.py.
# Biến chỉ dùng khi thử: XUONG_NGUON (thư mục mã có sẵn), XUONG_MAY (nơi đặt phần mềm), XUONG_GOI (nhe|du).

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Dung($loi) { Write-Host ""; Write-Host "DỪNG: $loi" -ForegroundColor Red; exit 1 }

$BoNao = (Get-Location).Path
if (-not ((Test-Path (Join-Path $BoNao 'INDEX.md')) -and (Get-ChildItem $BoNao -Directory -Filter '01_*' -ErrorAction SilentlyContinue))) {
    Dung "Thư mục đang mở ($BoNao) không phải Bộ Não AI (cần có INDEX.md và ngăn 01_...). Mở Claude đúng thư mục Bộ Não AI rồi dán lại câu lệnh."
}

# Nơi đặt phần mềm: ngoài bộ não (bộ não có thể đồng bộ OneDrive/Drive). Ổ C còn dưới 6 GB thì sang ổ trống nhiều nhất.
$May = $env:XUONG_MAY
if (-not $May) {
    $May = Join-Path $env:LOCALAPPDATA 'XuongVideoAI'
    $trongC = (Get-PSDrive C).Free / 1GB
    if ($trongC -lt 6) {
        $o = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 -and $_.Name -ne 'C' } | Sort-Object Free -Descending | Select-Object -First 1
        if ($o -and ($o.Free / 1GB) -gt $trongC) { $May = "$($o.Name):\XuongVideoAI" }
    }
}
New-Item -ItemType Directory -Force -Path $May | Out-Null
Write-Host "Bộ não: $BoNao"
Write-Host "Phần mềm của xưởng đặt ở: $May"

# 1. uv
$UvDir = Join-Path $May 'uv'
$Uv = Join-Path $UvDir 'uv.exe'
if (-not (Test-Path $Uv)) {
    Write-Host "Tải uv (trình quản lý Python, khoảng 20 MB)..."
    $zip = Join-Path $May 'uv.zip'
    Invoke-WebRequest -UseBasicParsing 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' -OutFile $zip
    Expand-Archive -Force $zip $UvDir
    Remove-Item $zip
}
try { & $Uv --version | Out-Null } catch { Dung "Windows chặn chạy uv.exe ($Uv). Thường do Smart App Control hoặc phần mềm diệt virus. Chụp màn hình gửi người hướng dẫn." }

# 2. Python 3.12 riêng cho xưởng (không đụng Python có sẵn trên máy).
# Dùng bản chính hãng python.org (gói NuGet, có chữ ký số): Smart App Control của Windows 11 chặn Python do uv tải về (thử 25/11/2026).
$env:UV_CACHE_DIR = Join-Path $May 'uv-cache'
$PyBan = '3.12.10'
$PyGoc = Join-Path $May "python-$PyBan"
$Venv = Join-Path $May 'venv'
$Py = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path $Py)) {
    if (-not (Test-Path (Join-Path $PyGoc 'tools\python.exe'))) {
        Write-Host "Tải Python $PyBan chính hãng (python.org, khoảng 15 MB)..."
        $zip = Join-Path $May 'python.zip'
        Invoke-WebRequest -UseBasicParsing "https://www.nuget.org/api/v2/package/python/$PyBan" -OutFile $zip
        Expand-Archive -Force $zip $PyGoc
        Remove-Item $zip
    }
    Write-Host "Tạo môi trường Python riêng cho xưởng..."
    & (Join-Path $PyGoc 'tools\python.exe') -m venv --without-pip $Venv
    if ($LASTEXITCODE -or -not (Test-Path $Py)) { Dung "Không tạo được Python cho xưởng. Chụp màn hình gửi người hướng dẫn." }
}
try { & $Py -c "print(1)" | Out-Null } catch { Dung "Windows chặn chạy Python của xưởng ($Py). Chụp màn hình gửi người hướng dẫn." }

# 3. Mã xưởng
$Nguon = $env:XUONG_NGUON
if (-not $Nguon) {
    Write-Host "Tải mã Xưởng Video AI từ GitHub..."
    $zip = Join-Path $May 'nguon.zip'
    Invoke-WebRequest -UseBasicParsing 'https://codeload.github.com/ductuenam/xuong-video-ai/zip/refs/heads/main' -OutFile $zip
    $tam = Join-Path $May 'nguon-moi'
    if (Test-Path $tam) { Remove-Item -Recurse -Force $tam }
    Expand-Archive -Force $zip $tam
    Remove-Item $zip
    $Nguon = Join-Path $May 'nguon'
    if (Test-Path $Nguon) { Remove-Item -Recurse -Force $Nguon }
    Move-Item (Get-ChildItem $tam -Directory | Select-Object -First 1).FullName $Nguon
    Remove-Item -Recurse -Force $tam
}

# 4. Phần chính (chung cho Windows và Mac)
$thamSo = @('-X', 'utf8', (Join-Path $Nguon 'cai\cai_xuong.py'), '--bo-nao', $BoNao, '--may', $May, '--nguon', $Nguon, '--uv', $Uv)
if ($env:XUONG_GOI) { $thamSo += @('--goi', $env:XUONG_GOI) }
& $Py @thamSo
exit $LASTEXITCODE
