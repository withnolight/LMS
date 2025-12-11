import ctypes
import sqlite3
import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox

def adjust_treeview_column_widths(tree, min_padding=50):
    import tkinter as tk
    import tkinter.font as tkFont

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

def book_query():
    win = tk.Toplevel()
    win.title("查询书籍状态")
    win.geometry("1200x600")

    ttk.Label(win, text="输入书名或作者或ISBN", font=("Microsoft YaHei", 14)).pack(pady=30)

    # 新建一行的 Frame
    input_frame = tk.Frame(win)
    input_frame.pack(pady=10)

    entry = ttk.Entry(input_frame, width=50)
    entry.pack(side=tk.LEFT, padx=5)

    button = ttk.Button(input_frame, text="查询", 
                        command=lambda: search_books(entry.get(), tree))
    button.pack(side=tk.LEFT, padx=5)

    # TreeView 在下面
    columns = ("ID", "书名", "作者", "出版社", "年份", "ISBN", "类别", "库存量")
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=tk.BOTH, expand=True, pady=20)

def search_books(query, tree):
    """根据查询条件搜索书籍并更新树视图"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT books.id, books.title, books.author, books.publisher, books.year,
               books.isbn, categories.name AS category, books.copies
        FROM books
        LEFT JOIN categories ON books.category_id = categories.id
        WHERE books.title LIKE ? OR books.author LIKE ? OR books.isbn LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    results = cursor.fetchall()
    conn.close()

    # 清空现有数据
    for item in tree.get_children():
        tree.delete(item)

    # 插入新数据
    for row in results:
        tree.insert("", tk.END, values=row)
    
    adjust_treeview_column_widths(tree)

def borrow_query():
    win = tk.Toplevel()
    win.title("查询借阅记录")
    win.geometry("800x400")

    ttk.Label(win, text="输入读者ID或书名", font=("Microsoft YaHei", 14)).pack(pady=30)

    # 新建一行的 Frame
    input_frame = tk.Frame(win)
    input_frame.pack(pady=10)

    entry = ttk.Entry(input_frame, width=50)
    entry.pack(side=tk.LEFT, padx=5)

    button = ttk.Button(input_frame, text="查询", 
                        command=lambda: search_borrows(entry.get(), tree))
    button.pack(side=tk.LEFT, padx=5)

    # TreeView 在下面
    columns = ("借阅ID", "读者ID", "书名", "副本ID", "借阅日期", "归还日期", "归还状态")
    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=tk.BOTH, expand=True, pady=20)

def search_borrows(query, tree):
    """根据查询条件搜索借阅记录并更新树视图"""
    conn = sqlite3.connect("database.db")
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
    conn.close()

    # 清空现有数据
    for item in tree.get_children():
        tree.delete(item)

    # 插入新数据
    for row in results:
        tree.insert("", tk.END, values=row)

    adjust_treeview_column_widths(tree)

def open_operation_window(number):
    """打开一个新的操作窗口"""
    win = tk.Toplevel()
    win.title(f"操作窗口 {number}")
    win.geometry("300x150")

    ttk.Label(win, text=f"这里是操作窗口 {number}", font=("Arial", 14)).pack(pady=30)
    ttk.Button(win, text="关闭", command=win.destroy).pack()

def book_borrow():
    win = tk.Toplevel()
    win.title("借书")
    win.geometry("600x400")

    ttk.Label(win, text="请输入借书信息", font=("Microsoft YaHei", 16)).pack(pady=25)

    # ====== 表单区域（用 grid 更好看） ======
    form = tk.Frame(win)
    form.pack(pady=20)

    # 第一行：读者 ID
    ttk.Label(form, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_user_id = ttk.Entry(form, width=35)
    entry_user_id.grid(row=0, column=1, padx=10, pady=10)

    # 第二行：副本 ID
    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_book_id = ttk.Entry(form, width=35)
    entry_book_id.grid(row=1, column=1, padx=10, pady=10)

    # 第三行：按钮（居中）
    button = ttk.Button(form, text="借书",
                        command=lambda: execute_borrow(entry_user_id.get(), entry_book_id.get()))
    button.grid(row=2, column=0, columnspan=2, pady=20)

def execute_borrow(user_id, book_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 检查副本是否可借
    cursor.execute("SELECT status, borrowable FROM copies WHERE id=?", (book_id,))
    result01 = cursor.fetchone()
    cursor.execute("SELECT maxborrow, borrowed_count FROM users WHERE id=?", (user_id,))
    result02 = cursor.fetchone()

    result= result01 and (result02[1] < result02[0])

    if not result:
        if not result02:
            messagebox.showerror("错误", "读者ID不存在或已达借书上限！")
        else:
            messagebox.showerror("错误", "副本ID不存在！")
    else:
        status, borrowable = result01
        if status != 'available' or borrowable == 0:
            messagebox.showerror("错误", "该副本不可借！")
        else:
            # 执行借书操作
            cursor.execute("""
                INSERT INTO borrows (user_id, copy_id)
                VALUES (?, ?)
            """, (user_id, book_id))

            # 更新副本状态
            cursor.execute("""
                UPDATE copies
                SET status='borrowed'
                WHERE id=?
            """, (book_id,))
            # 更新用户已借书数量
            cursor.execute("""
                UPDATE users
                SET borrowed_count = borrowed_count + 1
                WHERE id=?
            """, (user_id,))

            conn.commit()
            messagebox.showinfo("成功", "借书成功！")

    conn.close()
    win = tk.Toplevel()
    win.title("借书")

def book_return():
    win = tk.Toplevel()
    win.title("还书")
    win.geometry("600x400")

    ttk.Label(win, text="请输入还书信息", font=("Microsoft YaHei", 16)).pack(pady=25)

    # ====== 表单区域（用 grid 更好看） ======
    form = tk.Frame(win)
    form.pack(pady=20)

    # 第一行：读者 ID
    ttk.Label(form, text="读者ID：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_user_id = ttk.Entry(form, width=35)
    entry_user_id.grid(row=0, column=1, padx=10, pady=10)

    # 第二行：副本 ID
    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_book_id = ttk.Entry(form, width=35)
    entry_book_id.grid(row=1, column=1, padx=10, pady=10)

    # 第三行：按钮（居中）
    button = ttk.Button(form, text="还书",
                        command=lambda: execute_return(entry_user_id.get(), entry_book_id.get()))
    button.grid(row=2, column=0, columnspan=2, pady=20)

def execute_return(user_id, book_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 检查借阅记录是否存在且未归还
    cursor.execute("""
        SELECT id FROM borrows
        WHERE user_id=? AND copy_id=? AND returned=0
    """, (user_id, book_id))
    borrow_record = cursor.fetchone()

    if not borrow_record:
        messagebox.showerror("错误", "无效的借阅记录或该书已归还！")
    else:
        borrow_id = borrow_record[0]

        # 执行还书操作
        cursor.execute("""
            UPDATE borrows
            SET returned=1, return_date=CURRENT_TIMESTAMP
            WHERE id=?
        """, (borrow_id,))

        # 更新副本状态
        cursor.execute("""
            UPDATE copies
            SET status='available'
            WHERE id=?
        """, (book_id,))

        # 更新用户已借书数量
        cursor.execute("""
            UPDATE users
            SET borrowed_count = borrowed_count - 1
            WHERE id=?
        """, (user_id,))

        conn.commit()
        messagebox.showinfo("成功", "还书成功！")

    conn.close()

def book_add():
    win = tk.Toplevel()
    win.title("新增书籍")
    win.geometry("600x700")
    ttk.Label(win, text="请输入新增书籍信息", font=("Microsoft YaHei", 16)).pack(pady=25)
    # ====== 表单区域（用 grid 更好看） ======
    form = tk.Frame(win)
    form.pack(pady=20)
    # 第一行：书名
    ttk.Label(form, text="书名：", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_title = ttk.Entry(form, width=35)
    entry_title.grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(form, text="作者：", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_author = ttk.Entry(form, width=35)
    entry_author.grid(row=1, column=1, padx=10, pady=10)
    ttk.Label(form, text="出版社：", font=("Microsoft YaHei", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_publisher = ttk.Entry(form, width=35)
    entry_publisher.grid(row=2, column=1, padx=10, pady=10)
    ttk.Label(form, text="年份：", font=("Microsoft YaHei", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_year = ttk.Entry(form, width=35)
    entry_year.grid(row=3, column=1, padx=10, pady=10)
    ttk.Label(form, text="ISBN：", font=("Microsoft YaHei", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_ISBN = ttk.Entry(form, width=35)
    entry_ISBN.grid(row=4, column=1, padx=10, pady=10)
    ttk.Label(form, text="简介：", font=("Microsoft YaHei", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    entry_description = ttk.Entry(form, width=35)
    entry_description.grid(row=5, column=1, padx=10, pady=10)
    ttk.Label(form, text="类别ID：", font=("Microsoft YaHei", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="e")
    entry_category_id = ttk.Entry(form, width=35)
    entry_category_id.grid(row=6, column=1, padx=10, pady=10)
    ttk.Label(form, text="新增本数：", font=("Microsoft YaHei", 12)).grid(row=7, column=0, padx=10, pady=10, sticky="e")
    entry_copies = ttk.Entry(form, width=35)
    entry_copies.grid(row=7, column=1, padx=10, pady=10)
    frame01= tk.Frame(form)
    frame01.grid(row=8, column=1, padx=10, pady=10, sticky="w")
    borrowable_var = tk.IntVar(value=1)
    ttk.Checkbutton(frame01, text="是否可借", variable=borrowable_var).pack(side=tk.RIGHT)
    # 第三行：按钮（居中）
    button = ttk.Button(frame01, text="新增书籍",
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
    button.pack(side=tk.LEFT, padx=10)

def execute_add_book(title, author, publisher, year, isbn, description, category_id, copies, borrowable):
    #先检查是否存在该种书，如果存在则只增加副本数量，不存在需要先新增书籍记录
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, copies FROM books WHERE isbn=?", (isbn,))
    result = cursor.fetchone()
    if result:
        book_id, current_copies = result
        new_copies = current_copies + int(copies)
        cursor.execute("UPDATE books SET copies=? WHERE id=?", (new_copies, book_id))
        for i in range(int(copies)):
            cursor.execute("INSERT INTO copies (book_id, status, location, borrowable) VALUES (?, 'available', '默认位置', ?)", (book_id, borrowable))
    else:
        cursor.execute("""
            INSERT INTO books (title, author, publisher, year, description, category_id, isbn, copies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, publisher, year, description, category_id, isbn, copies))
        book_id = cursor.lastrowid
        for i in range(int(copies)):
            cursor.execute("INSERT INTO copies (book_id, status, location, borrowable) VALUES (?, 'available', '默认位置', ?)", (book_id, borrowable))
    conn.commit()
    conn.close()
    messagebox.showinfo("成功", "书籍新增成功！")

def book_damage():
    win = tk.Toplevel()
    win.title("书籍报损")
    win.geometry("600x400")
    ttk.Label(win, text="请输入报损副本ID", font=("Microsoft YaHei", 16)).pack(pady=25)
    # ====== 表单区域（用 grid 更好看） ======
    form = tk.Frame(win)
    form.pack(pady=20)
    # 第一行：副本 ID
    ttk.Label(form, text="副本ID：", font=("Microsoft YaHei",12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_copy_id = ttk.Entry(form, width=35)
    entry_copy_id.grid(row=0, column=1, padx=10, pady=10)
    # 第二行：按钮（居中）
    button = ttk.Button(form, text="标记为报损",
                        command=lambda: marked_as_damaged(entry_copy_id.get()))
    button.grid(row=1, column=0, columnspan=2, pady=10)

def marked_as_damaged(copy_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 检查副本是否存在
    cursor.execute("SELECT status FROM copies WHERE id=?", (copy_id,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("错误", "副本ID不存在！")
    else:
        status = result[0]
        if status == 'damaged':
            messagebox.showinfo("提示", "该副本已标记为报损！")
        else:
            # 标记为报损
            # 先查询是否是借出的状态，若是则需要先降低对应用户的已借书数量
            if status == 'borrowed':
                cursor.execute("""
                    SELECT user_id FROM borrows
                    WHERE copy_id=? AND returned=0
                """, (copy_id,))
                borrow_record = cursor.fetchone()
                if borrow_record:
                    user_id = borrow_record[0]
                    cursor.execute("""
                        UPDATE users
                        SET borrowed_count = borrowed_count - 1
                        WHERE id=?
                    """, (user_id,))
            cursor.execute("""
                UPDATE copies
                SET status='damaged', borrowable=0
                WHERE id=?
            """, (copy_id,))
            cursor.execute("""
                UPDATE books
                SET copies = copies - 1
                WHERE id = (SELECT book_id FROM copies WHERE id=?)
            """, (copy_id,))
            cursor.execute("""
                DELETE FROM borrows
                WHERE copy_id=? AND returned=0
            """, (copy_id,))
            conn.commit()
            messagebox.showinfo("成功", "副本已标记为报损！")

    conn.close()

def user_management():
    win = tk.Toplevel()
    win.title("读者管理")
    win.geometry("1600x800")
    ttk.Label(win, text="读者管理", font=("Microsoft YaHei", 16)).pack(pady=25)
    form = tk.Frame(win)
    form.pack(pady=20)
    frame01= tk.Frame(form)
    frame01.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    frame02= tk.Frame(form)
    frame02.grid(row=0, column=1, padx=10, pady=10,sticky="w")
    ##frame01放置读者新增和删除功能，frame02放置读者查询功能
    ttk.Label(frame01, text="读者新增", font=("Microsoft YaHei", 14)).pack()
    frame01_1= tk.Frame(frame01)
    frame01_1.pack(pady=10)
    ttk.Label(frame01_1, text="读者ID：", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
    entry_user_id = ttk.Entry(frame01_1, width=20)
    entry_user_id.pack(side=tk.LEFT, padx=5)
    frame01_2= tk.Frame(frame01)
    frame01_2.pack(pady=10)
    ttk.Label(frame01_2, text="用户名：", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
    entry_username = ttk.Entry(frame01_2, width=20)
    entry_username.pack(side=tk.LEFT, padx=5)
    frame01_3= tk.Frame(frame01)
    frame01_3.pack(pady=10)
    ttk.Label(frame01_3, text="密码：  ", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
    entry_password = ttk.Entry(frame01_3, width=20, show="*")
    entry_password.pack(side=tk.LEFT, padx=5)
    frame01_4= tk.Frame(frame01)
    frame01_4.pack(pady=10)
    ttk.Button(frame01_4, text="新增读者",
               command=lambda: add_user(entry_user_id.get(), entry_username.get(), entry_password.get())).pack(side=tk.LEFT, padx=5)

    ttk.Label(frame01, text="读者删除", font=("Microsoft YaHei", 14)).pack()
    frame01_5= tk.Frame(frame01)
    frame01_5.pack(pady=10)
    ttk.Label(frame01_5,text="读者ID:", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
    entry_delete_user_id = ttk.Entry(frame01_5, width=20)
    entry_delete_user_id.pack(side=tk.LEFT, padx=5)
    frame01_6= tk.Frame(frame01)
    frame01_6.pack(pady=10)
    ttk.Button(frame01_6, text="删除读者",
               command=lambda: delete_user(entry_delete_user_id.get())).pack(side=tk.LEFT, padx=5)
    
    ## 读者查询功能
    ttk.Label(frame02, text="读者查询", font=("Microsoft YaHei", 14)).pack()
    frame02_1= tk.Frame(frame02)
    frame02_1.pack(pady=10)
    ttk.Label(frame02_1, text="读者ID或用户名：", font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=5)
    entry_query = ttk.Entry(frame02_1, width=30)
    entry_query.pack(side=tk.LEFT, padx=5)
    button_query = ttk.Button(frame02_1, text="查询",
                        command=lambda: search_users(entry_query.get(), tree))
    button_query.pack(side=tk.LEFT, padx=5)
    # TreeView 在下面
    columns = ("ID", "用户名", "性别", "用户类型", "邮箱", "已借书数量", "最大可借数量")
    tree = ttk.Treeview(frame02, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True, pady=20)

def search_users(query, tree):
    """根据查询条件搜索读者并更新树视图"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, gender, user_type, email, borrowed_count, maxborrow
        FROM users
        WHERE id LIKE ? OR username LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()

    # 清空现有的树视图内容
    for item in tree.get_children():
        tree.delete(item)

    # 插入新的查询结果
    for row in results:
        tree.insert("", tk.END, values=row)
    
    adjust_treeview_column_widths(tree)

def add_user(user_id, username, password):
    conn= sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
                       (user_id, username, password))
        conn.commit()
        messagebox.showinfo("成功", "读者新增成功！")
    except sqlite3.IntegrityError:
        messagebox.showerror("错误", "读者ID已存在或其他信息有误！")
    conn.close()

def delete_user(user_id):
    conn= sqlite3.connect("database.db")
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
    conn.close()

def quit_application():
    answer = messagebox.askyesno("退出登录", "确定要退出登录吗？")
    if answer:
        tk._exit(0)

def update_clock(label):
    """实时更新时钟"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=f"当前时间：{now}")
    label.after(1000, update_clock, label)

def create_main_window(username):
    root = tk.Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    root.tk.call('tk',"scaling", ScaleFactor/75)
    style = ttk.Style()
    style.configure("Treeview", 
                rowheight = int(28 * float(ScaleFactor) / 96),
                font=("Microsoft YaHei", 9))
    root.title("主界面")
    root.geometry("400x600")

    # 登录用户显示
    user_label = ttk.Label(root, text=f"当前登录用户：{username}", font=("Arial", 14))
    user_label.pack(pady=10)

    bookcount = 0
    conn= sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    bookcount = cursor.fetchone()[0]


    user_label = ttk.Label(root, text=f"当前系统共有书籍数量：{bookcount}", font=("Arial", 12))
    user_label.pack(pady=10)
    conn.close()

    # 时钟
    clock_label = ttk.Label(root, text="", font=("Arial", 12))
    clock_label.pack(pady=10)
    update_clock(clock_label)

    # 操作按钮
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=40)

    ttk.Button(button_frame, text="查询书籍状态", width=20,
               command=lambda: book_query()).pack(pady=5)
    ttk.Button(button_frame, text="查询借阅记录", width=20,
               command=lambda: borrow_query()).pack(pady=5)
    ttk.Button(button_frame, text="借书", width=20,
               command=lambda: book_borrow()).pack(pady=5)
    ttk.Button(button_frame, text="还书", width=20,
               command=lambda: book_return()).pack(pady=5)
    ttk.Button(button_frame, text="新增书籍", width=20,
               command=lambda: book_add()).pack(pady=5)
    ttk.Button(button_frame, text="书籍报损", width=20,
               command=lambda: book_damage()).pack(pady=5)
    ttk.Button(button_frame, text="读者管理", width=20,
               command=lambda: user_management()).pack(pady=5)
    ttk.Button(button_frame, text="退出登录", width=20,
               command=lambda: quit_application()).pack(pady=5)
    root.mainloop()

# 示例：假设登录用户名是 admin

if __name__ == "__main__":
    username = "debug_admin"
    create_main_window(username)