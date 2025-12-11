# 📚 图书馆管理系统 (Library Management System)

一个基于Python和SQLite的现代化图书馆管理系统，具有友好的图形界面和完整的功能模块。

## ✨ 功能特性

- **用户管理**
  - 读者新增、删除和查询
  - 支持学生和教师两种身份
  - 不同身份的借书上限设置（学生3本，教师10本）

- **图书管理**
  - 新增书籍（支持同ISBN多本录入）
  - 查询书籍状态
  - 书籍报损处理
  - 自动管理书籍副本

- **借阅管理**
  - 借书功能
  - 还书功能
  - 借阅记录查询
  - 自动计算借阅数量

- **现代化界面**
  - 使用ttkbootstrap美化UI
  - 深色主题（Darkly）
  - 实时时钟显示
  - 响应式布局

## 📋 系统要求

- Python 3.7+
- Windows / macOS / Linux
- SQLite 3（通常随Python一起安装）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

第一次运行时，执行初始化脚本创建数据库表：

```bash
python init.py
```

这将创建以下表：
- `admin` - 管理员账户
- `users` - 读者信息
- `books` - 书籍信息
- `categories` - 书籍分类
- `copies` - 书籍副本
- `borrows` - 借阅记录
- `reservations` - 预约记录
- `reviews` - 评论评分

### 3. 启动应用

```bash
python start.py
```

## 📖 使用指南

### 登录界面
- 输入管理员用户名和密码
- 默认账户需要自行在数据库中添加

### 主菜单功能

| 功能 | 说明 |
|------|------|
| 查询书籍状态 | 按书名、作者或ISBN查询 |
| 查询借阅记录 | 按读者ID或书名查询 |
| 借书 | 输入读者ID和副本ID进行借书 |
| 还书 | 输入读者ID和副本ID进行还书 |
| 新增书籍 | 添加新书籍或增加已有书籍的副本 |
| 书籍报损 | 标记损坏的书籍 |
| 读者管理 | 新增、删除和查询读者 |
| 退出登录 | 退出系统 |

### 数据库初始化

首次使用前需要添加管理员账户：

```bash
python
>>> import sqlite3
>>> conn = sqlite3.connect('database.db')
>>> cursor = conn.cursor()
>>> cursor.execute("INSERT INTO admin (name, password, email) VALUES (?, ?, ?)", 
                   ("admin", "123456", "admin@example.com"))
>>> conn.commit()
>>> conn.close()
```

## 📁 项目结构

```
MMS/
├── init.py              # 数据库初始化脚本
├── start.py             # 登录界面
├── main.py              # 主程序
├── database.db          # SQLite数据库（首次运行后生成）
├── requirements.txt     # 依赖列表
└── README.md           # 项目说明文档
```

## 🗄️ 数据库设计

### 主要表结构

**users（读者表）**
```
id          BIGINT PRIMARY KEY      读者ID
username    TEXT NOT NULL           用户名
password    TEXT NOT NULL           密码
user_type   TEXT (student/teacher)  用户类型
email       TEXT UNIQUE             邮箱
borrowed_count INT DEFAULT 0        已借书数
maxborrow   INT DEFAULT 3           最大可借数
```

**books（书籍表）**
```
id          INTEGER PRIMARY KEY     书籍ID
title       TEXT NOT NULL           书名
author      TEXT                    作者
publisher   TEXT                    出版社
year        INTEGER                 出版年份
description TEXT                    书籍简介
category_id INTEGER                 分类ID
isbn        TEXT UNIQUE             ISBN号
copies      INTEGER DEFAULT 1       书籍总数
```

**borrows（借阅记录表）**
```
id          INTEGER PRIMARY KEY     借阅ID
user_id     BIGINT                  读者ID
copy_id     INTEGER                 副本ID
borrow_time DATETIME                借书时间
return_date DATETIME                归还时间
returned    INTEGER DEFAULT 0       归还状态
```

## ⚙️ 配置说明

### 修改学生/教师借书上限

在 `user_management()` 函数中的 `add_user()` 调用处修改：

```python
# 当前设置：学生3本，教师10本
maxborrow = 3 if user_type == 'student' else 10
```

### 修改主题

在 `create_main_window()` 函数中修改：

```python
# 可选主题: darkly, solar, superhero, cyborg, sandstone, flatly, minty, lumen, morph, journal, vapor
root = ttk.Window(themename="darkly")
```

## 🐛 常见问题

**Q: 无法连接数据库？**
A: 确保已运行 `init.py` 初始化数据库，且database.db文件在项目目录下。

**Q: 登录失败？**
A: 检查admin表中是否有数据，需要先手动添加管理员账户。

**Q: 图形界面显示混乱？**
A: Windows系统请确保已安装Microsoft YaHei字体，或修改代码中的字体设置。

## 📝 注意事项

1. **数据安全**：生产环境中密码应使用加密存储
2. **备份**：定期备份database.db文件
3. **并发**：SQLite在高并发场景下性能有限，生产环境建议迁移到MySQL/PostgreSQL
4. **日期时间**：系统使用SQLite的CURRENT_TIMESTAMP，确保服务器时间准确

## 🔧 开发者信息

- **语言**：Python 3.7+
- **GUI框架**：Tkinter + ttkbootstrap
- **数据库**：SQLite 3
- **许可证**：GNU GPLv3
