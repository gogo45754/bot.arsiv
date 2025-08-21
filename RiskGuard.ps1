param(
  [ValidateSet('Enforce','Unlock')]
  [string]$Mode = 'Enforce'
)

$ErrorActionPreference = 'Stop'

# Proje köküne geç (dosya nerede ise orası)
Set-Location -Path $PSScriptRoot

# logs klasörü dursun
if (-not (Test-Path '.\logs')) {
  New-Item -ItemType Directory -Path '.\logs' | Out-Null
}

# UTF-8 sabitle
$env:PYTHONUTF8       = '1'
$env:PYTHONIOENCODING = 'utf-8'

# Yollar
$py     = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python.exe' }      # (yedek) sistem Python
$target = Join-Path $PSScriptRoot 'risk_guard.py'
$log    = Join-Path $PSScriptRoot 'logs\risk_guard.log'

# Geçici çıktı dosyaları (Start-Process için zorunlu)
$logOut = Join-Path $PSScriptRoot 'logs\risk_guard.out.tmp'
$logErr = Join-Path $PSScriptRoot 'logs\risk_guard.err.tmp'

$action = if ($Mode -eq 'Unlock') { '--unlock' } else { '--enforce' }

Write-Host "Python: $py"
Write-Host "Target: $target"
Write-Host "Action: $action"
Write-Host "Log: $log"

# Çalıştır: stdout ve stderr'i ayrı dosyalara yaz
Start-Process -FilePath $py `
  -ArgumentList @($target, $action) `
  -NoNewWindow `
  -RedirectStandardOutput $logOut `
  -RedirectStandardError  $logErr `
  -Wait

# Birleştir + temizle
Get-Content -Path $logOut -Encoding utf8 | Add-Content -Path $log
Get-Content -Path $logErr -Encoding utf8 | Add-Content -Path $log
Remove-Item $logOut, $logErr -ErrorAction SilentlyContinue

# Son 50 satırı göster
Write-Host "`n--- Son 50 satır ---`n" -ForegroundColor Green
Get-Content -Path $log -Tail 50 -Encoding utf8
