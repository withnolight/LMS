import sys
import sqlite3
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from init import DB_PATH


# --------------- 通用工具函数 ---------------

def get_connection():
    """获取数据库连接（启用外键约束）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def adjust_treeview_column_widths(tree, min_padding=50):
    columns = tree["columns"]
    font = tkFont.Font(font=("Microsoft YaHei", 11))

    for col in columns:
        max_width = font.measure(col)

        for item in tree.get_children():
            text = str(tree.set(item, col))
            width = font.measure(text)
            if width > max_width:
                max_width = width

        tree.column(col, width=max_width + min_padding)


def refresh_treeview(tree, rows):
    """清空并重新填充 Treeview"""
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", END, values=row)
    adjust_treeview_column_widths(tree)

def book_query():
    win = ttk.Toplevel()
    win.title("查询书籍状态")
    win.geometry("1200x600")

    ttk.Label(win, text="输入书名或作者或ISBN", font=("Microsoft YaHei", 14)).pack(pady=30)

    input_frame = ttk.Frame(win)
    input_frame.pack(pady=10)

    entry = ttk.Entry(input_frame, width=50)
    entry.pack(side=LEFT, padx=5)

    button = ttk.Button(input_frame, text="查询", 
                        command=lambda: search_books(entry.get(), tree), bootstyle="info")
    button.pack(side=LEFT, padx=5)

    columns = ("ID", "书名", "作者", "出版社", "年份", "ISBN", "类别", "库存量")
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=BOTH, expand=True, pady=20)

def search_books(query, tree):
    """根据查询条件搜索书籍并更新树视图"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT books.id, books.title, books.author, books.publisher, books.year,
                   books.isbn, categories.name AS category, books.copies
            FROM books
            LEFT JOIN categories ON books.category_id = categories.id
            WHERE books.title LIKE ? OR books.author LIKE ? OR books.isbn LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()

    refresh_treeview(tree, results)

def borrow_query():
    win = ttk.Toplevel()
    win.title("查询借阅记录")
    win.geometry("1200x600")

    ttk.Label(win, text="输入读者ID或书名", font=("Microsoft YaHei", 14)).pack(pady=30)

    input_frame = ttk.Frame(win)
    input_frame.pack(pady=10)

    entry = ttk.Entry(input_frame, width=50)
    entry.pack(side=LEFT, padx=5)

    button = ttk.Button(input_frame, text="查询", 
                        command=lambda: search_borrows(entry.get(), tree), bootstyle="info")
    button.pack(side=LEFT, padx=5)

    columns = ("借阅ID", "读者ID", "书名", "副本ID", "借阅日期", "归还日期", "归还状态")
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill=BOTH, expand=True, pady=20)

def search_borrows(query, tree):
    """根据查询条件搜索借阅记录并更新树视图"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT borrows.id, borrows.user_id, books.title, borrows.copy_id,
                   borrows.borrow_time, borrows.return_date, borrows.returned
            FROM borrows
            LEFT JOIN copies ON borrows.copy_id = copies.id
            LEFT JOIN books  ON copies.book_id = books.id
            WHERE borrows.user_id LIKE ? OR books.title LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()

    refresh_treeview(tree, results)

def book_borrow():
    win = ttk.Toplevel()
    win.title("借书")
    win.geometry("600x400")

    ttk.Label(win, text="请输入借书信息", font=("Microsoft YaHei", 16)).pack(pady=25)

    form = ttk.Frame(win)
    form.pack(pady=20)

    ttk.Label(form, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky=E)
    entry_user_id = ttk.Entry(form, width=35)
    entry_user_id.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=E)
    entry_book_id = ttk.Entry(form, width=35)
    entry_book_id.grid(row=1, column=1, padx=10, pady=10)

    button = ttk.Button(form, text="借书", bootstyle="success",
                        command=lambda: execute_borrow(entry_user_id.get(), entry_book_id.get()))
    button.grid(row=2, column=0, columnspan=2, pady=20)

def execute_borrow(user_id, book_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT status, borrowable FROM copies WHERE id=?", (book_id,))
        copy_info = cursor.fetchone()
        cursor.execute("SELECT maxborrow, borrowed_count FROM users WHERE id=?", (user_id,))
        user_info = cursor.fetchone()

        if not user_info:
            messagebox.showerror("错误", "读者ID不存在！")
            return
        if not copy_info:
            messagebox.showerror("错误", "副本ID不存在！")
            return
        if user_info[1] >= user_info[0]:
            messagebox.showerror("错误", "该读者已达借书上限！")
            return

        status, borrowable = copy_info
        if status != 'available' or borrowable == 0:
            messagebox.showerror("错误", "该副本不可借！")
            return

        cursor.execute("""
            INSERT INTO borrows (user_id, copy_id)
            VALUES (?, ?)
        """, (user_id, book_id))
        cursor.execute("""
            UPDATE copies SET status='borrowed' WHERE id=?
        """, (book_id,))
        cursor.execute("""
            UPDATE users SET borrowed_count = borrowed_count + 1 WHERE id=?
        """, (user_id,))

        conn.commit()
        messagebox.showinfo("成功", "借书成功！")

def book_return():
    win = ttk.Toplevel()
    win.title("还书")
    win.geometry("600x400")

    ttk.Label(win, text="请输入还书信息", font=("Microsoft YaHei", 16)).pack(pady=25)

    form = ttk.Frame(win)
    form.pack(pady=20)

    ttk.Label(form, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky=E)
    entry_user_id = ttk.Entry(form, width=35)
    entry_user_id.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=E)
    entry_book_id = ttk.Entry(form, width=35)
    entry_book_id.grid(row=1, column=1, padx=10, pady=10)

    button = ttk.Button(form, text="还书", bootstyle="warning",
                        command=lambda: execute_return(entry_user_id.get(), entry_book_id.get()))
    button.grid(row=2, column=0, columnspan=2, pady=20)

def execute_return(user_id, book_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM borrows
            WHERE user_id=? AND copy_id=? AND returned=0
        """, (user_id, book_id))
        borrow_record = cursor.fetchone()

        if not borrow_record:
            messagebox.showerror("错误", "无效的借阅记录或该书已归还！")
            return

        borrow_id = borrow_record[0]
        cursor.execute("""
            UPDATE borrows SET returned=1, return_date=CURRENT_TIMESTAMP WHERE id=?
        """, (borrow_id,))
        cursor.execute("""
            UPDATE copies SET status='available' WHERE id=?
        """, (book_id,))
        cursor.execute("""
            UPDATE users SET borrowed_count = borrowed_count - 1 WHERE id=?
        """, (user_id,))

        conn.commit()
        messagebox.showinfo("成功", "还书成功！")

def book_add():
    win = ttk.Toplevel()
    win.title("新增书籍")
    win.geometry("600x700")
    ttk.Label(win, text="请输入新增书籍信息", font=("Microsoft YaHei", 16)).pack(pady=25)
    
    form = ttk.Frame(win)
    form.pack(pady=20)
    
    ttk.Label(form, text="书名：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky=E)
    entry_title = ttk.Entry(form, width=35)
    entry_title.grid(row=0, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="作者：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=E)
    entry_author = ttk.Entry(form, width=35)
    entry_author.grid(row=1, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="出版社：", font=("Microsoft YaHei", 12)).grid(row=2, column=0, padx=10, pady=10, sticky=E)
    entry_publisher = ttk.Entry(form, width=35)
    entry_publisher.grid(row=2, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="年份：", font=("Microsoft YaHei", 12)).grid(row=3, column=0, padx=10, pady=10, sticky=E)
    entry_year = ttk.Entry(form, width=35)
    entry_year.grid(row=3, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="ISBN：", font=("Microsoft YaHei", 12)).grid(row=4, column=0, padx=10, pady=10, sticky=E)
    entry_ISBN = ttk.Entry(form, width=35)
    entry_ISBN.grid(row=4, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="简介：", font=("Microsoft YaHei", 12)).grid(row=5, column=0, padx=10, pady=10, sticky=E)
    entry_description = ttk.Entry(form, width=35)
    entry_description.grid(row=5, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="类别ID：", font=("Microsoft YaHei", 12)).grid(row=6, column=0, padx=10, pady=10, sticky=E)
    entry_category_id = ttk.Entry(form, width=35)
    entry_category_id.grid(row=6, column=1, padx=10, pady=10)
    
    ttk.Label(form, text="新增本数：", font=("Microsoft YaHei", 12)).grid(row=7, column=0, padx=10, pady=10, sticky=E)
    entry_copies = ttk.Entry(form, width=35)
    entry_copies.grid(row=7, column=1, padx=10, pady=10)
    
    frame01 = ttk.Frame(form)
    frame01.grid(row=8, column=1, padx=10, pady=10, sticky=W)
    borrowable_var = tk.IntVar(value=1)
    ttk.Checkbutton(frame01, text="是否可借", variable=borrowable_var).pack(side=LEFT)
    
    button = ttk.Button(frame01, text="新增书籍", bootstyle="success",
                        command=lambda: execute_add_book(
                            entry_title.get(),
                            entry_author.get(),
                            entry_publisher.get(),
                            entry_year.get(),
                            entry_ISBN.get(),
                            entry_description.get(),
                            entry_category_id.get(),
                            entry_copies.get(),
                            borrowable_var.get()
                        ))
    button.pack(side=LEFT, padx=10)

def execute_add_book(title, author, publisher, year, isbn, description, category_id, copies, borrowable):
    num_copies = int(copies)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, copies FROM books WHERE isbn=?", (isbn,))
        result = cursor.fetchone()

        if result:
            book_id, current_copies = result
            cursor.execute("UPDATE books SET copies=? WHERE id=?",
                           (current_copies + num_copies, book_id))
        else:
            cursor.execute("""
                INSERT INTO books (title, author, publisher, year, description, category_id, isbn, copies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, author, publisher, year, description, category_id, isbn, num_copies))
            book_id = cursor.lastrowid

        for _ in range(num_copies):
            cursor.execute(
                "INSERT INTO copies (book_id, status, location, borrowable) VALUES (?, 'available', '默认位置', ?)",
                (book_id, borrowable))

        conn.commit()
    messagebox.showinfo("成功", "书籍新增成功！")

def book_damage():
    win = ttk.Toplevel()
    win.title("书籍报损")
    win.geometry("600x400")
    ttk.Label(win, text="请输入报损副本ID", font=("Microsoft YaHei", 16)).pack(pady=25)
    
    form = ttk.Frame(win)
    form.pack(pady=20)
    
    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei",12)).grid(row=0, column=0, padx=10, pady=10, sticky=E)
    entry_copy_id = ttk.Entry(form, width=35)
    entry_copy_id.grid(row=0, column=1, padx=10, pady=10)
    
    button = ttk.Button(form, text="标记为报损", bootstyle="danger",
                        command=lambda: marked_as_damaged(entry_copy_id.get()))
    button.grid(row=1, column=0, columnspan=2, pady=10)

def marked_as_damaged(copy_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM copies WHERE id=?", (copy_id,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("错误", "副本ID不存在！")
            return

        status = result[0]
        if status == 'damaged':
            messagebox.showinfo("提示", "该副本已标记为报损！")
            return

        if status == 'borrowed':
            cursor.execute("""
                SELECT user_id FROM borrows
                WHERE copy_id=? AND returned=0
            """, (copy_id,))
            borrow_record = cursor.fetchone()
            if borrow_record:
                cursor.execute("""
                    UPDATE users SET borrowed_count = borrowed_count - 1 WHERE id=?
                """, (borrow_record[0],))

        cursor.execute("""
            UPDATE copies SET status='damaged', borrowable=0 WHERE id=?
        """, (copy_id,))
        cursor.execute("""
            UPDATE books SET copies = copies - 1
            WHERE id = (SELECT book_id FROM copies WHERE id=?)
        """, (copy_id,))
        cursor.execute("""
            DELETE FROM borrows WHERE copy_id=? AND returned=0
        """, (copy_id,))

        conn.commit()
        messagebox.showinfo("成功", "副本已标记为报损！")

def user_management():
    win = ttk.Toplevel()
    win.title("读者管理")
    win.geometry("1600x800")
    ttk.Label(win, text="读者管理", font=("Microsoft YaHei", 16)).pack(pady=25)
    form = ttk.Frame(win)
    form.pack(pady=20)
    frame01 = ttk.Frame(form)
    frame01.grid(row=0, column=0, padx=10, pady=10, sticky=W)
    frame02 = ttk.Frame(form)
    frame02.grid(row=0, column=1, padx=10, pady=10, sticky=W)
    
    ttk.Label(frame01, text="读者新增", font=("Microsoft YaHei", 14)).grid(row=0, column=0, columnspan=2, pady=(0,10), sticky=W)

    ttk.Label(frame01, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, sticky=E, padx=5, pady=5)
    entry_user_id = ttk.Entry(frame01, width=25)
    entry_user_id.grid(row=1, column=1, sticky=W, padx=5)

    ttk.Label(frame01, text="用户名：", font=("Microsoft YaHei", 12)).grid(row=2, column=0, sticky=E, padx=5, pady=5)
    entry_username = ttk.Entry(frame01, width=25)
    entry_username.grid(row=2, column=1, sticky=W, padx=5)

    ttk.Label(frame01, text="密码：", font=("Microsoft YaHei", 12)).grid(row=3, column=0, sticky=E, padx=5, pady=5)
    entry_password = ttk.Entry(frame01, width=25, show="*")
    entry_password.grid(row=3, column=1, sticky=W, padx=5)

    ttk.Label(frame01, text="邮箱：", font=("Microsoft YaHei", 12)).grid(row=4, column=0, sticky=E, padx=5, pady=5)
    entry_email = ttk.Entry(frame01, width=25)
    entry_email.insert(0, "可选")
    entry_email.grid(row=4, column=1, sticky=W, padx=5)

    ttk.Label(frame01, text="身份：", font=("Microsoft YaHei", 12)).grid(row=5, column=0, sticky=E, padx=5, pady=5)
    combo_usertype = ttk.Combobox(frame01, width=22, state="readonly")
    combo_usertype["values"] = ["student", "teacher"]
    combo_usertype.current(0)
    combo_usertype.grid(row=5, column=1, sticky=W, padx=5)

    btn_add = ttk.Button(
        frame01,
        text="新增读者",
        bootstyle="success",
        command=lambda: add_user(
            entry_user_id.get(),
            entry_username.get(),
            entry_password.get(),
            combo_usertype.get(),
            entry_email.get() if entry_email.get() != "可选" else None
        )
    )
    btn_add.grid(row=6, column=0, columnspan=2, pady=10)

    ttk.Label(frame01, text="读者删除", font=("Microsoft YaHei", 14)).grid(row=7, column=0, columnspan=2, pady=(20,10), sticky=W)

    ttk.Label(frame01, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=8, column=0, sticky=E, padx=5, pady=5)
    entry_delete_user_id = ttk.Entry(frame01, width=25)
    entry_delete_user_id.grid(row=8, column=1, sticky=W, padx=5)

    btn_delete = ttk.Button(
        frame01,
        text="删除读者",
        bootstyle="danger",
        command=lambda: delete_user(entry_delete_user_id.get())
    )
    btn_delete.grid(row=9, column=0, columnspan=2, pady=10)

    ttk.Label(frame02, text="读者查询", font=("Microsoft YaHei", 14)).pack()
    frame02_1 = ttk.Frame(frame02)
    frame02_1.pack(pady=10)
    ttk.Label(frame02_1, text="读者ID或用户名：", font=("Microsoft YaHei", 12)).pack(side=LEFT, padx=5)
    entry_query = ttk.Entry(frame02_1, width=30)
    entry_query.pack(side=LEFT, padx=5)
    button_query = ttk.Button(frame02_1, text="查询", bootstyle="info",
                        command=lambda: search_users(entry_query.get(), tree))
    button_query.pack(side=LEFT, padx=5)
    
    columns = ("ID", "用户名", "用户类型", "邮箱", "已借书数量", "最大可借数量")
    tree = ttk.Treeview(frame02, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180)
    tree.pack(fill=BOTH, expand=True, pady=20)

def search_users(query, tree):
    """根据查询条件搜索读者并更新树视图"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, user_type, email, borrowed_count, maxborrow
            FROM users
            WHERE id LIKE ? OR username LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()

    refresh_treeview(tree, results)

def add_user(user_id, username, password, user_type, email):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (id, username, password, user_type, email, maxborrow) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, password, user_type, email, 3 if user_type == 'student' else 10))
            conn.commit()
            messagebox.showinfo("成功", "读者新增成功！")
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "读者ID已存在或其他信息有误！")

def delete_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT borrowed_count FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("错误", "读者ID不存在！")
        elif result[0] > 0:
            messagebox.showerror("错误", "该读者有未归还的书籍，无法删除！")
        else:
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            messagebox.showinfo("成功", "读者删除成功！")

def quit_application(root):
    answer = messagebox.askyesno("退出登录", "确定要退出登录吗？")
    if answer:
        root.destroy()
        sys.exit(0)

def update_clock(label):
    """实时更新时钟"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=f"当前时间：{now}")
    label.after(1000, update_clock, label)

def create_main_window(username):
    root = ttk.Window(themename="darkly")
    root.title("图书管理系统")
    root.geometry("500x700")

    ttk.Label(root, text=f"当前登录用户：{username}", font=("Microsoft YaHei", 14)).pack(pady=15)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        bookcount = cursor.fetchone()[0]

    ttk.Label(root, text=f"系统共有书籍数量：{bookcount}", font=("Microsoft YaHei", 12)).pack(pady=10)

    clock_label = ttk.Label(root, text="", font=("Microsoft YaHei", 11))
    clock_label.pack(pady=10)
    update_clock(clock_label)

    button_frame = ttk.Frame(root)
    button_frame.pack(pady=30, padx=20, fill=BOTH, expand=True)

    ttk.Button(button_frame, text="查询书籍状态", width=25, bootstyle="info",
               command=book_query).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="查询借阅记录", width=25, bootstyle="info",
               command=borrow_query).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="借书", width=25, bootstyle="success",
               command=book_borrow).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="还书", width=25, bootstyle="warning",
               command=book_return).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="新增书籍", width=25, bootstyle="success",
               command=book_add).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="书籍报损", width=25, bootstyle="danger",
               command=book_damage).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="读者管理", width=25, bootstyle="primary",
               command=user_management).pack(pady=5, fill=X)
    ttk.Button(button_frame, text="退出登录", width=25, bootstyle="danger-outline",
               command=lambda: quit_application(root)).pack(pady=5, fill=X)
    root.mainloop()

if __name__ == "__main__":
    username = "debug_admin"
    create_main_window(username)