# CMS prototype one-click start (MySQL 3307 + Django)
# MySQL data/config uses ASCII path under LOCALAPPDATA to avoid Chinese-path bugs.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
$MysqlBin = 'D:\Program Files\MySQL\MySQL Server 9.1\bin'
$Mysqld = Join-Path $MysqlBin 'mysqld.exe'
$Mysql = Join-Path $MysqlBin 'mysql.exe'
$MysqlHome = Join-Path $env:LOCALAPPDATA 'cms_prototype_mysql'
$Ini = Join-Path $MysqlHome 'my.ini'
$DataDir = Join-Path $MysqlHome 'data'
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

function Invoke-Mysql([string[]]$ExtraArgs, [string]$Sql) {
    # mysql writes errors to stderr; do not let PowerShell treat that as terminating
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & $Mysql -h 127.0.0.1 -P 3307 --protocol=tcp @ExtraArgs -e $Sql 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old
    return @{ Code = $code; Output = $out }
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Green
Write-Host '  CMS Prototype Starting' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''

if (-not (Test-Path $VenvPython)) {
    Write-Host 'ERROR: venv not found (.venv)' -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $Mysqld)) {
    Write-Host "ERROR: MySQL not found: $Mysqld" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $MysqlHome)) { New-Item -ItemType Directory -Path $MysqlHome | Out-Null }
if (-not (Test-Path $Ini)) {
    $dataUnix = ($DataDir -replace '\\', '/')
    $homeUnix = ($MysqlHome -replace '\\', '/')
    $iniText = @"
[mysqld]
basedir=D:/Program Files/MySQL/MySQL Server 9.1
datadir=$dataUnix
port=3307
mysqlx=0
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-storage-engine=INNODB
max_connections=50
innodb_buffer_pool_size=128M
log-error=$homeUnix/mysql3307.err

[client]
port=3307
default-character-set=utf8mb4
"@
    Set-Content -Path $Ini -Value $iniText -Encoding ASCII
}

if (-not (Test-Port 3307)) {
    if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir | Out-Null }
    if (-not (Test-Path (Join-Path $DataDir 'mysql'))) {
        Write-Host 'INFO: initializing MySQL datadir on 3307 ...' -ForegroundColor Cyan
        & $Mysqld --initialize-insecure --basedir='D:\Program Files\MySQL\MySQL Server 9.1' --datadir="$DataDir"
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'ERROR: MySQL initialize failed' -ForegroundColor Red
            exit 1
        }
    }
    Write-Host 'INFO: starting MySQL 3307 ...' -ForegroundColor Cyan
    Start-Process -FilePath $Mysqld -ArgumentList "--defaults-file=$Ini", '--console' -WindowStyle Hidden
    $ready = $false
    for ($i = 1; $i -le 45; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Port 3307) { $ready = $true; break }
    }
    if (-not $ready) {
        Write-Host 'ERROR: MySQL 3307 not ready' -ForegroundColor Red
        $err = Join-Path $MysqlHome 'mysql3307.err'
        if (Test-Path $err) { Get-Content $err -Tail 40 }
        exit 1
    }
    Write-Host 'OK: MySQL 3307 is running' -ForegroundColor Green
} else {
    Write-Host 'SKIP: MySQL 3307 already running' -ForegroundColor DarkYellow
}

Write-Host 'INFO: preparing database cms_prototype ...' -ForegroundColor Cyan

$setupSql = @"
CREATE DATABASE IF NOT EXISTS cms_prototype DEFAULT CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY '$DbPassword';
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DbPassword';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED BY '$DbPassword';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
"@

# Prefer password login (normal case after first setup)
$r = Invoke-Mysql @('-u', 'root', "-p$DbPassword") $setupSql
if ($r.Code -ne 0) {
    # Fallback: first-time insecure empty password
    Write-Host 'INFO: password login failed, trying empty password once ...' -ForegroundColor DarkYellow
    $r2 = Invoke-Mysql @('-u', 'root') "ALTER USER 'root'@'localhost' IDENTIFIED BY '$DbPassword'; CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY '$DbPassword'; ALTER USER 'root'@'127.0.0.1' IDENTIFIED BY '$DbPassword'; CREATE DATABASE IF NOT EXISTS cms_prototype DEFAULT CHARACTER SET utf8mb4; GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION; GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION; FLUSH PRIVILEGES;"
    if ($r2.Code -ne 0) {
        Write-Host 'ERROR: cannot connect MySQL 3307 / create database' -ForegroundColor Red
        Write-Host ($r.Output | Out-String)
        Write-Host ($r2.Output | Out-String)
        exit 1
    }
    $r = Invoke-Mysql @('-u', 'root', "-p$DbPassword") "CREATE DATABASE IF NOT EXISTS cms_prototype DEFAULT CHARACTER SET utf8mb4;"
    if ($r.Code -ne 0) {
        Write-Host 'ERROR: create database failed after setting password' -ForegroundColor Red
        Write-Host ($r.Output | Out-String)
        exit 1
    }
}

Write-Host 'OK: database ready' -ForegroundColor Green

Set-Location -LiteralPath $Root
Write-Host 'INFO: migrate ...' -ForegroundColor Cyan
& $VenvPython manage.py migrate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'INFO: init demo data ...' -ForegroundColor Cyan
& $VenvPython manage.py init_demo
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ''
Write-Host '----------------------------------------'
Write-Host ' Login:    http://127.0.0.1:8000/login/'
Write-Host ' Register: http://127.0.0.1:8000/register/'
Write-Host ' Accounts: super/1  admin/1  user01/1'
Write-Host ' MySQL:    127.0.0.1:3307  db=cms_prototype  pwd=123456'
Write-Host '----------------------------------------'
Write-Host ''
Write-Host 'INFO: starting Django runserver ...' -ForegroundColor Cyan
Start-Process 'http://127.0.0.1:8000/login/'
& $VenvPython manage.py runserver 0.0.0.0:8000
