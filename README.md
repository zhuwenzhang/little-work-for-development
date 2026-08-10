# CMS 原型系统 — VS Code 运行说明

## 一键启动
用 VS Code / Cursor 打开桌面 `小作业` 文件夹，终端执行：

```powershell
.\start.bat
```

或：

```powershell
.\start.ps1
```

会自动：
1. 启动独立 MySQL（端口 **3307**，不占用 3306）
2. 创建数据库 `cms_prototype`
3. 迁移表结构并写入演示数据
4. 启动 Django：http://127.0.0.1:8000/login/

> MySQL 数据目录在英文路径：`%LOCALAPPDATA%\cms_prototype_mysql\`  
> （避免中文路径导致 mysqld 读配置失败）

## 演示账号
| 用户ID | 密码 | 登录身份选择 | 说明 |
|--------|------|--------------|------|
| super  | 1    | 管理员       | 超级用户，可管普通用户+管理员 |
| admin  | 1    | 管理员       | 管理员，可管普通用户 |
| user01 | 1    | 普通用户     | 前台浏览与三种查询 |

也可自行注册普通用户。

## 已实现功能对照
- `user_app` / `category` / `item` 三张表（MySQL）
- 注册（仅普通用户，ID 冲突提示）
- 登录（可选普通用户/管理员，按类型跳转）
- 普通用户：文章列表/详情 + 按题目/时间/栏目查询
- 管理员：栏目/文章增删改查
- 用户管理：管理员管普通用户；超管还可管管理员

## 数据库连接
`config/settings.py`：
- Host: `127.0.0.1`
- Port: `3307`
- Database: `cms_prototype`
- User: `root`
- Password: `123456`

## 拓展功能
- 用户: 可以发表评论
- 管理员：不能删除但是可以不显示该评论
