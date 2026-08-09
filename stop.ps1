# CMS prototype one-click stop (Django :8000 + MySQL :3307 homework instance)
# Does NOT stop Windows service MySQL91 / port 3306.
$ErrorActionPreference = 'Continue'
$MysqlBin = 'D:\Program Files\MySQL\MySQL Server 9.1\bin'
$Mysqladmin = Join-Path $MysqlBin 'mysqladmin.exe'
$MysqlHome = Join-Path $env:LOCALAPPDATA 'cms_prototype_mysql'
$DbPassword = '123456'

function Test-Port([int]$Port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(400)
        if ($ok -and $client.Connected) { $client.Close(); return $true }
        $client.Close()
        return $false
    } catch { return $false }
}

function Stop-PortListeners([int]$Port, [string]$Label) {
    $killed = $false
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            $procId = $c.OwningProcess
            if ($procId -and $procId -ne 0) {
                $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "STOP: $Label (PID=$procId, $($proc.ProcessName))" -ForegroundColor Cyan
                    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                    $killed = $true
                }
            }
        }
    } catch {}

    # Fallback: kill python runserver related to this project
    if (-not $killed -and $Port -eq 8000) {
        Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.CommandLine -and ($_.CommandLine -match 'manage\.py\s+runserver')) {
                Write-Host "STOP: Django runserver (PID=$($_.ProcessId))" -ForegroundColor Cyan
                Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
                $killed = $true
            }
        }
    }

    if (-not $killed) {
        Write-Host "SKIP: $Label not running" -ForegroundColor DarkYellow
    }
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Yellow
Write-Host '  CMS Prototype Stopping' -ForegroundColor Yellow
Write-Host '========================================' -ForegroundColor Yellow
Write-Host ''

Stop-PortListeners 8000 'Django'

# Stop homework MySQL on 3307 only (datadir under LOCALAPPDATA\cms_prototype_mysql)
$cmsMysqld = Get-CimInstance Win32_Process -Filter "Name='mysqld.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -and (
            $_.CommandLine -match 'cms_prototype_mysql' -or
            $_.CommandLine -match 'port[= ]3307' -or
            ($_.CommandLine -match '3307' -and $_.CommandLine -match 'defaults-file')
        )
    }

if (-not $cmsMysqld -and (Test-Port 3307)) {
    # If 3307 is listening, treat it as the homework instance
    $cmsMysqld = Get-CimInstance Win32_Process -Filter "Name='mysqld.exe'" -ErrorAction SilentlyContinue
}

if ($cmsMysqld -or (Test-Port 3307)) {
    Write-Host 'STOP: MySQL 3307 (mysqladmin shutdown)...' -ForegroundColor Cyan
    if (Test-Path $Mysqladmin) {
        $old = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $Mysqladmin -h 127.0.0.1 -P 3307 --protocol=tcp -u root "-p$DbPassword" shutdown 2>$null | Out-Null
        $ErrorActionPreference = $old
        Start-Sleep -Seconds 2
    }

    # Force kill remaining homework mysqld if still up
    $left = Get-CimInstance Win32_Process -Filter "Name='mysqld.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and (
                $_.CommandLine -match 'cms_prototype_mysql' -or
                $_.CommandLine -match 'port[= ]3307'
            )
        }
    if ($left) {
        Write-Host 'STOP: MySQL 3307 (force kill)...' -ForegroundColor Cyan
        $left | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    }

    if (Test-Port 3307) {
        Write-Host 'WARN: port 3307 still listening' -ForegroundColor Red
    } else {
        Write-Host 'OK: MySQL 3307 stopped' -ForegroundColor Green
    }
} else {
    Write-Host 'SKIP: MySQL 3307 not running (system MySQL91 untouched)' -ForegroundColor DarkYellow
}

Write-Host ''
Write-Host 'All CMS services stopped.' -ForegroundColor Green
Write-Host ''