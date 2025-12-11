import sqlite3
import random
import string
from datetime import datetime, timedelta

DB = "database.db"

def random_text(n=8):
    return ''.join(random.choices(string.ascii_letters, k=n))

def random_email():
    return random_text(6) + "@example.com"

def random_chinese(n=4):
    return ''.join(chr(random.randint(0x4e00, 0x9fa5)) for _ in range(n))

def fill_test_data():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # ---------------------------
    # 1. 管理员
    # ---------------------------
    admins = [
        ("admin1", "pass123", random_email()),
        ("admin2", "pass123", random_email()),
        ("admin3", "pass123", random_email()),
    ]
    cursor.executemany(
        "INSERT INTO admin (name, password, email) VALUES (?, ?, ?)",
        admins
    )

    # ---------------------------
    # 2. 生成用户（7 学生 + 3 老师）
    # ---------------------------
    users = []
    for i in range(7):
        users.append((
            20250001 + i,                         # id
            f"student{i+1}",
            random.choice(["男", "女"]),
            "123456",
            "student",
            random_email(),
            0, 3
        ))
    for i in range(3):
        users.append((
            20260001 + i,
            f"teacher{i+1}",
            random.choice(["男", "女"]),
            "123456",
            "teacher",
            random_email(),
            0, 5        # 老师能借更多
        ))

    cursor.executemany('''
        INSERT INTO users(id, username, gender, password, user_type, email, borrowed_count, maxborrow)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # ---------------------------
    # 3. 分类
    # ---------------------------
    categories = ["计算机", "文学", "科学", "历史", "艺术"]
    category_ids = []

    for name in categories:
        cursor.execute("INSERT INTO categories(name) VALUES(?)", (name,))
        category_ids.append(cursor.lastrowid)

    # ---------------------------
    # 4. 生成书（20 本）
    # ---------------------------
    book_ids = []
    for i in range(20):
        title = "《" + random_chinese(random.randint(3, 6)) + "》"
        author = random_chinese(3)
        publisher = random_text(6)
        year = random.randint(1980, 2024)
        desc = f"{title} 的简介……"
        cat_id = random.choice(category_ids)
        isbn = f"ISBN{10000000 + i}"

        cursor.execute('''
            INSERT INTO books(title, author, publisher, year, description, category_id, isbn, copies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, publisher, year, desc, cat_id, isbn, random.randint(1, 3)))

        book_ids.append(cursor.lastrowid)

    # ---------------------------
    # 5. 生成副本表（1 每本书 1～3 副本）
    # ---------------------------
    copy_ids = []
    for book_id in book_ids:
        n = cursor.execute("SELECT copies FROM books WHERE id=?", (book_id,)).fetchone()[0]
        for _ in range(n):
            cursor.execute('''
                INSERT INTO copies(book_id, status, location, borrowable)
                VALUES (?, 'available', ?, 1)
            ''', (book_id, "图书区-" + random.choice(["A", "B", "C", "D"])))
            copy_ids.append(cursor.lastrowid)

    # ---------------------------
    # 6. 生成 100 条借阅记录
    # ---------------------------
    user_ids = [u[0] for u in users]

    for _ in range(100):
        user = random.choice(user_ids)
        copy = random.choice(copy_ids)

        # 随机借阅日期（过去一年内）
        borrow_time = datetime.now() - timedelta(days=random.randint(0, 365))
        borrow_time_str = borrow_time.strftime("%Y-%m-%d %H:%M:%S")

        returned = random.choice([0, 1])

        if returned:
            return_time = borrow_time + timedelta(days=random.randint(1, 30))
            return_time_str = return_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return_time_str = None

        cursor.execute('''
            INSERT INTO borrows(user_id, copy_id, borrow_time, return_date, returned)
            VALUES (?, ?, ?, ?, ?)
        ''', (user, copy, borrow_time_str, return_time_str, returned))

    conn.commit()
    conn.close()
    print("测试数据填充完成！")

fill_test_data()
