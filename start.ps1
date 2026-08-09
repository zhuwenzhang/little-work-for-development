# CMS 原型系统一键启动（MySQL 3307 + Django）
# 注意：MySQL 配置/数据放在纯英文路径，避免中文目录导致 defaults-file 解析失败
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
$MysqlBin = 'D:\Program Files\MySQL\MySQL Server 9.1\bin'
$Mysqld = Join-Path $MysqlBin 'mysqld.exe'
$Mysql = Join-Path $MysqlBin 'mysql.exe'
$MysqlHome = Join-Path $env:LOCALAPPDATA 'cms_prototype_mysql'
$Ini = Join-Path $MysqlHome 'my.ini'
$DataDir = Join-Path $MysqlHome 'data'

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

Write-Host ''
Write-Host '========================================' -ForegroundColor Green
Write-Host '  CMS 原型系统启动' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''

if (-not (Test-Path $VenvPython)) {
    Write-Host '[错误] 未找到虚拟环境' -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $Mysqld)) {
    Write-Host "[错误] 未找到 MySQL: $Mysqld" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $MysqlHome)) { New-Item -ItemType Directory -Path $MysqlHome | Out-Null }
if (-not (Test-Path $Ini)) {
    @"
[mysqld]
basedir=D:/Program Files/MySQL/MySQL Server 9.1
datadir=$($DataDir -replace '\\','/')
port=3307
mysqlx=0
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-storage-engine=INNODB
max_connections=50
innodb_buffer_pool_size=128M
log-error=$($MysqlHome -replace '\\','/')/mysql3307.err

[client]
port=3307
default-character-set=utf8mb4
"@ | Set-Content -Path $Ini -Encoding ASCII
}

if (-not (Test-Port 3307)) {
    if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir | Out-Null }
    if (-not (Test-Path (Join-Path $DataDir 'mysql'))) {
        Write-Host '[初始化] MySQL 数据目录 (3307)...' -ForegroundColor Cyan
        & $Mysqld --initialize-insecure --basedir='D:\Program Files\MySQL\MySQL Server 9.1' --datadir="$DataDir"
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[错误] MySQL 初始化失败' -ForegroundColor Red
            exit 1
        }
    }
    Write-Host '[启动] MySQL 3307 ...' -ForegroundColor Cyan
    Start-Process -FilePath $Mysqld -ArgumentList "--defaults-file=$Ini", '--console' -WindowStyle Hidden
    $ready = $false
    for ($i = 1; $i -le 45; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Port 3307) { $ready = $true; break }
    }
    if (-not $ready) {
        Write-Host '[错误] MySQL 3307 未能就绪' -ForegroundColor Red
        $err = Join-Path $MysqlHome 'mysql3307.err'
        if (Test-Path $err) { Get-Content $err -Tail 40 }
        exit 1
    }
    Write-Host '[完成] MySQL 3307 已启动' -ForegroundColor Green
} else {
    Write-Host '[跳过] MySQL 3307 已在运行' -ForegroundColor DarkYellow
}

Write-Host '[准备] 数据库 cms_prototype ...' -ForegroundColor Cyan
# 先尝试无密码（首次 initialize-insecure）
& $Mysql -h 127.0.0.1 -P 3307 -u root --protocol=tcp -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '123456'; CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY '123456'; CREATE DATABASE IF NOT EXISTS cms_prototype DEFAULT CHARACTER SET utf8mb4; GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION; GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION; FLUSH PRIVILEGES;" 2>$null
& $Mysql -h 127.0.0.1 -P 3307 -u root -p123456 --protocol=tcp -e "CREATE DATABASE IF NOT EXISTS cms_prototype DEFAULT CHARACTER SET utf8mb4;" 
if ($LASTEXITCODE -ne 0) {
    Write-Host '[错误] 无法连接 MySQL 3307 / 创建数据库' -ForegroundColor Red
    exit 1
}

Set-Location -LiteralPath $Root
Write-Host '[迁移] 执行 migrate ...' -ForegroundColor Cyan
& $VenvPython manage.py migrate
Write-Host '[数据] 初始化演示数据 ...' -ForegroundColor Cyan
& $VenvPython manage.py init_demo

Write-Host ''
Write-Host '----------------------------------------'
Write-Host ' 登录页: http://127.0.0.1:8000/login/'
Write-Host ' 注册页: http://127.0.0.1:8000/register/'
Write-Host ' 演示账号: super/1  admin/1  user01/1'
Write-Host ' MySQL: 127.0.0.1:3307  库 cms_prototype  密码 123456'
Write-Host '----------------------------------------'
Write-Host ''
Write-Host '[启动] Django runserver ...' -ForegroundColor Cyan
Start-Process 'http://127.0.0.1:8000/login/'
& $VenvPython manage.py runserver 0.0.0.0:8000
