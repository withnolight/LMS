import sqlite3
import tkinter
#####################
#   图书馆管理系统   #
#####################
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()  # 连接到数据库
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''' ) # 创建管理员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            gender TEXT,
            password TEXT NOT NULL,
            user_type TEXT DEFAULT 'student',
            email TEXT UNIQUE,
            maxborrow INTEGER DEFAULT 3
        )
    ''')  # 创建用户表

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            publisher TEXT,
            year INTEGER,
            description TEXT,
            category_id INTEGER,
            isbn TEXT UNIQUE,
            copies INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')  # 创建图书表

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS copies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            status TEXT DEFAULT 'available',
            location TEXT,
            borrowable INTEGER DEFAULT 1,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''') # 创建图书副本表

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            copy_id INTEGER,
            borrow_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            return_date DATETIME,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (copy_id) REFERENCES copies(id)
        )
    ''')  # 创建借阅记录表

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            book_id INTEGER,
            reservation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            fulfilled INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')  # 创建预约表

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT,
                book_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT DEFAULT 'GOOD!',
                review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
    ''')

    conn.commit()
    conn.close()

init_db()